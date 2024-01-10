import logging
import json

class Manifest:
    """
    Manifest class to CRUD the file
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.dict = self.load_manifest()
        self.structure =  {
            "connection_name": None,
            "created_at": None,
            "last_seen_at": None,
            "margin": None,
            "expected_uplink_interval_sec": None,
            "connection_type": None,
            "lorawandevice": {
                "deveui": None,
                "name": None,
                "battery_level": None,
                "labels": None,
                "serial_no": None,
                "uri": None,
                "hardware": {
                    "hardware": None,
                    "hw_model": None,
                    "hw_version": None,
                    "sw_version": None,
                    "manufacturer": None,
                    "datasheet": None,
                    "capabilities": None,
                    "description": None,
                },
            }
        }

    def load_manifest(self):
        """
        Return manifest based on filepath
        """
        with open(self.filepath, 'r') as f:
            return json.load(f)

    def save_manifest(self):
        """
        Save manifest file
        """
        with open(self.filepath, 'w') as f:
            json.dump(self.dict, f, indent=3)

    def lc_check(self) -> bool:
        """
        Check if there is a lorawan connection array in Manifest
        """
        return "lorawanconnections" in self.dict

    def ld_search(self, deveui: str) -> bool:
        """
        Search the manifest for a lorawan device return true if found
        """
        #consider using a bloom filter: if the count of lorawan connections gets to be a 
        # huge number the computation will be too high - Francisco Lozano 01/09/2024
        if self.lc_check():
            for lc in self.dict["lorawanconnections"]:
                ld = lc["lorawandevice"]
                if ld["deveui"] == deveui:
                    return True 
        else:
            return False
        return False

    @staticmethod
    def is_valid_json(data: dict) -> bool:
        """
        Check for valid json format
        """
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError as e:
            logging.error(f"is_valid_json: {e}")
            return False

    def check_keys(self, data: dict, structure: dict) -> bool:
        """
        A recursive function that iterates through the keys defined in the structure.
        If a key is a dict, it recursively checks the nested keys. 
        """
        return all(key in data and (type(data[key]) == dict and self.check_keys(data[key], structure[key]) if isinstance(structure[key], dict) else True) for key in structure)

    def is_valid_struc(self, data: dict) -> bool:
        """
        Checks if the data conforms to manifest structure
        """
        if self.is_valid_json(data):
            json_data = data
        else:
            return False

        return self.check_keys(json_data, self.structure)
            
    def has_requiredKeys(self, data: dict) -> bool:
        """
        Check if data has required keys
        """
        if self.is_valid_json(data):
            json_data = data
        else:
            return False

        try:
            # Check if required keys are present
            required_keys = [
                "connection_type", 
                "lorawandevice"
            ]
            for key in required_keys:
                if key not in json_data:
                    return False

            # Check if "lorawandevice" has the required keys
            lorawandevice_keys = [
                "deveui",
                "name", 
                "hardware"
            ]
            for key in lorawandevice_keys:
                if key not in json_data["lorawandevice"]:
                    return False

            # Check if "hardware" has the required keys
            hardware_keys = ["hw_model"]
            for key in hardware_keys:
                if key not in json_data["lorawandevice"]["hardware"]:
                    return False

            # If all checks passed, return True
            return True

        except (TypeError, KeyError) as e:
            # Handle exceptions if the structure is not as expected
            logging.error(f"is_valid_lc: {e}")
            return False

    def update_manifest(self, data: dict):
        """
        Update manifest with new lorawan connection data
        """
        if not self.is_valid_struc(data):
            logging.error("update_manifest: lorawan connection data does not conform to manifest structure")
            return
        
        if not self.lc_check():
            # If "lorawanconnections" is not present, create it as an empty list
            self.dict["lorawanconnections"] = []

        existing_lcs = self.dict["lorawanconnections"]
        new_lc = data

        # Find the index of the connection based on a uid
        index_to_update = next((i for i, existing_lc in enumerate(existing_lcs) 
                                if existing_lc.get("lorawandevice", {}).get("deveui") == new_lc.get("lorawandevice", {}).get("deveui")), None)

        if index_to_update is not None:
            # Update the existing connection
            existing_lcs[index_to_update].update(new_lc)
        else:
            # If not found, check for required keys and add the new connection
            if not self.has_requiredKeys(data):
                logging.error("update_manifest: lorawan connection data does not have required keys")
                return
            existing_lcs.append(new_lc)

        # Save the updated manifest
        self.save_manifest()

        return