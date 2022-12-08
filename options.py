from waifu2x_vulkan import waifu2x_vulkan


class options():
    available_upscale_methods = ["waifu2x_vulkan", "ESRGAN_4x"]
    chosen_upscale_method = ""
    upscale_method = ""
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