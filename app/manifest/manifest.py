import logging
import json

class Manifest:
    """
    Manifest class to CRUD the file
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.dict = self.load_manifest()

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

    @staticmethod
    def is_valid_lc(data: dict) -> bool:
        """
        Check if data conforms to manifest structure
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
        if not self.is_valid_lc(data):
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
            # If not found, add the new connection
            existing_lcs.append(new_lc)

        # Save the updated manifest
        self.save_manifest()

        return

    #TODO: do I need seperate functions to update lorawan devices, hardware, and connections in manifest?
    #   The update_manifest function takes care of updating everyting. If I use update_manifest,
    #   I will need to make sure the input 'data' follows the correct json convention 

    # def update_ld(self):
    #     """
    #     update lorawan device in manifest
    #     """
    #     return

    # def create_ld(self):
    #     """
    #     create lorawan device in manifest
    #     """
    #     return

    # def update_sh(self):
    #     """
    #     update sensor hardware in manifest
    #     """
    #     return

    # def create_sh(self):
    #     """
    #     create sensor hardware in manifest
    #     """
    #     return