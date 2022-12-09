from waifu2x_vulkan import waifu2x_vulkan


class options():
    available_upscale_methods = ["waifu2x_vulkan", "ESRGAN_4x"]
    chosen_upscale_method = ""
    upscale_method = ""
    max_resolution = 2048
    waifu2x_vulkan_model_noise_level_1 = [waifu2x_vulkan.MODEL_ANIME_STYLE_ART_RGB_NOISE1, waifu2x_vulkan.MODEL_CUNET_NOISE1, 
                                           waifu2x_vulkan.MODEL_CUNET_NO_SCALE_NOISE1, waifu2x_vulkan.MODEL_PHOTO_NOISE1]
    waifu2x_vulkan_model_noise_level_2 = [waifu2x_vulkan.MODEL_ANIME_STYLE_ART_RGB_NOISE2, waifu2x_vulkan.MODEL_CUNET_NOISE2,
                                          waifu2x_vulkan.MODEL_CUNET_NO_SCALE_NOISE2, waifu2x_vulkan.MODEL_PHOTO_NOISE2]
    waifu2x_vulkan_model_noise_level_3 = [waifu2x_vulkan.MODEL_ANIME_STYLE_ART_RGB_NOISE3, waifu2x_vulkan.MODEL_CUNET_NOISE3,
                                          waifu2x_vulkan.MODEL_CUNET_NO_SCALE_NOISE3, waifu2x_vulkan.MODEL_PHOTO_NOISE3]
    waifu2x_vulkan_model_noise_level = 1
    chosen_waifu2x_vulkan_model = None
    upscale_factor = 2
    game_base_dir = ""
    quickbms_executable = ""
    available_dat_files = ["model.dat", "weapon.dat", "map.dat"]
    dat_files_chosen = []

    def load_from_file(self, file_path):
        with open(file_path, "r") as f:
            self.chosen_upscale_method = f.readline().strip()
            self.max_resolution = int(f.readline().strip())
            self.waifu2x_vulkan_model_noise_level = int(f.readline().strip())
            self.chosen_waifu2x_vulkan_model = int(f.readline().strip())
            self.upscale_factor = int(f.readline().strip())
            self.game_base_dir = f.readline().strip()
            self.quickbms_executable = f.readline().strip()
            self.dat_files_chosen = f.readline().strip().split(",")
        
    # save to file and overwrite existing file
    def save_to_file(self, file_path):
        with open(file_path, "w") as f:
            f.write(self.chosen_upscale_method + "\n")
            f.write(str(self.max_resolution) + "\n")
            f.write(str(self.waifu2x_vulkan_model_noise_level) + "\n")
            f.write(str(self.chosen_waifu2x_vulkan_model) + "\n")
            f.write(str(self.upscale_factor) + "\n")
            f.write(self.game_base_dir + "\n")
            f.write(self.quickbms_executable + "\n")
            f.write(",".join(self.dat_files_chosen) + "\n")
            

class tracked_progress():
    file_id = 0
    chosen_options = options()

    def load_from_file(self, file_path):
        with open(file_path, "r") as f:
            self.file_id = int(f.readline())
            self.chosen_options.load_from_file(f.readline().strip())
    
    # save to file and overwrite existing file
    def save_to_file(self, file_path):
        with open(file_path, "w") as f:
            f.write(str(self.file_id) + "\n")
            f.write("options.txt" + "\n")
            self.chosen_options.save_to_file("options.txt")

        
    