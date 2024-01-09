class Manifest:
    """
    Manifest class to CRUD the file
    """
    def __init__(self, path: str):
        self.dict = self.get_manifest(path)

    def get_manifest(self, path: str) -> dict:
        """
        Return manifest based on file path input
        """
        with open(self.args.manifest) as f:
            manifest = json.load(f)
        
        return manifest

    def lc_check(self) -> bool:
        """
        Check if there is a lorawan connection array in Manifest
        """
        return "lorawanconnections" in self.dict

    def ld_search(self, uid: str) -> bool:
        """
        Search the manifest for a lorawan device return true if found
        """
        #consider using a bloom filter: if the count of lorawan connections gets to be a 
        # huge number the computation will be too high - Francisco Lozano 01/09/2024
        if self.lc_check():
            for lc in self.dict["lorawanconnections"]:
                ld = lc["lorawandevice"]
                if ld["deveui"] == uid:
                    return True 
        else:
            return False
        return False

    def update_lc(self):
        """
        update lorawan connection in manifest
        """
        return

    def create_lc(self):
        """
        create lorawan connection in manifest
        """
        return

    def update_ld(self):
        """
        update lorawan device in manifest
        """
        return

    def create_ld(self):
        """
        create lorawan device in manifest
        """
        return

    def update_sh(self):
        """
        update sensor hardware in manifest
        """
        return

    def create_sh(self):
        """
        create sensor hardware in manifest
        """
        return