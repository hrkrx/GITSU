from logging import getLogger, StreamHandler
import subprocess
import threading
import shutil
import time
import os
try: import kivy
except: subprocess.run(["pip", "install", "kivy"])
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.clock import mainthread
from kivy.uix.popup import Popup
from kivy.uix.button import Button 
from kivy.uix.label import Label
from kivy.app import App
try: import waifu2x_vulkan
except: subprocess.run(["pip", "install", "waifu2x-vulkan"])
from waifu2x_vulkan import waifu2x_vulkan
from io import StringIO
from unpacker import *
from upscaler import *
from options import *
from dds import *

#########################
#       Constants       #
#########################

log_stream = StringIO()
console = StreamHandler(log_stream)
log = getLogger()

temp_path = "temp/"

working_dir = os.path.abspath(os.getcwd())

# starts a thread with a callback that updates the progress bar
def start_thread(callback):
    thread = threading.Thread(target=callback)
    thread.start()

class SettingsPopup(Popup):
    chosen_options = options()
    has_error = False
    cancelled = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # sets the default values for the settings
        self.chosen_options.chosen_upscale_method = "waifu2x_vulkan"
        self.chosen_options.waifu2x_vulkan_model_noise_level = 1
        self.chosen_options.chosen_waifu2x_vulkan_model = waifu2x_vulkan.MODEL_ANIME_STYLE_ART_RGB_NOISE1
        self.chosen_options.upscale_factor = 2
        self.chosen_options.game_base_dir = "PATH\\TO_GAME_FOLDER\\2094209"
        self.chosen_options.quickbms_executable = "PATH\\TO\\quickbms_4gb_files.exe"

        self.ids.waifu_vulkan_checkbox.active = True
        self.ids.quickbms_path_textinput.text = self.chosen_options.quickbms_executable
        self.ids.game_path_textinput.text = self.chosen_options.game_base_dir
    
    def get_options(self):
        return self.app.chosen_options

    # sets the method used to upscale the images, and validates the input with the available methods
    def set_upscale_method(self, method):
        if method in self.chosen_options.available_upscale_methods:
            self.chosen_options.chosen_upscale_method = method
            self.ids.specific_model_settings.clear_widgets()
            if method == "waifu2x_vulkan":
                # grid layout for the waifu2x_vulkan method specific settings
                waifu2x_vulkan_grid = GridLayout(rows=3)
                
                # build the waifu2x_vulkan method specific settings
                noise_level_grid = GridLayout(cols=2, size_hint_y=None, height=30)
                noise_level_grid.add_widget(Label(text="Noise Level:", size_hint_x=0.5))
                noise_level_spinner = Spinner(text="1", values=("1", "2", "3"), size_hint_y=None, height=30)
                noise_level_spinner.bind(text=self.noise_level_spinner_text_changed)
                noise_level_grid.add_widget(noise_level_spinner)
                waifu2x_vulkan_grid.add_widget(noise_level_grid)

                # add the model dropdown
                model_grid = GridLayout(cols=2, size_hint_y=None, height=30)
                model_grid.add_widget(Label(text="Model:", size_hint_x=0.5))
                model_spinner = Spinner(text="MODEL_ANIME_STYLE_ART_RGB", values=("MODEL_ANIME_STYLE_ART_RGB", "MODEL_CUNET", "MODEL_CUNET_NO_SCALE", "MODEL_PHOTO"), size_hint_y=None, height=30)
                model_spinner.bind(text=self.model_spinner_text_changed)
                model_grid.add_widget(model_spinner)
                waifu2x_vulkan_grid.add_widget(model_grid)

                # add upscale factor spinner
                upscale_factor_grid = GridLayout(cols=2, size_hint_y=None, height=30)
                upscale_factor_grid.add_widget(Label(text="Upscale Factor:", size_hint_x=0.5))
                upscale_factor_spinner = Spinner(text="2", values=("2", "3", "4"), size_hint_y=None, height=30)
                upscale_factor_spinner.bind(text=self.upscale_factor_spinner_text_changed)
                upscale_factor_grid.add_widget(upscale_factor_spinner)
                waifu2x_vulkan_grid.add_widget(upscale_factor_grid)

                self.ids.specific_model_settings.add_widget(waifu2x_vulkan_grid)

            elif method == "ESRGAN_4x":
                # build the ESRGAN_4x method specific settings
                warning_label = Label(text="Warning: ESRGAN_4x is extremly demanding on your GPU/CPU (16GB VRAM for GPU or 20GB RAM for CPU required), and will take a long time.")
                warning_label.wrap = True
                warning_label.size_hint_y = None
                warning_label.text_size = (self.width - 25, None)
                self.ids.specific_model_settings.add_widget(warning_label)

        else:
            log.error(f"Settings: {method} is not a valid upscale method")
            self.has_error = True
    
    def noise_level_spinner_text_changed(self, spinner, text):
        self.set_waifu2x_vulkan_noise_level(int(text))
    
    def model_spinner_text_changed(self, spinner, text):
        # set the model based on the noise level and the selected model
        if self.chosen_options.waifu2x_vulkan_model_noise_level == 1:
            if text == "MODEL_ANIME_STYLE_ART_RGB":
                self.set_waifu2x_vulkan_model(waifu2x_vulkan.MODEL_ANIME_STYLE_ART_RGB_NOISE1)
            elif text == "MODEL_CUNET":
                self.set_waifu2x_vulkan_model(waifu2x_vulkan.MODEL_CUNET_NOISE1)
            elif text == "MODEL_CUNET_NO_SCALE":
                self.set_waifu2x_vulkan_model(waifu2x_vulkan.MODEL_CUNET_NO_SCALE_NOISE1)
            elif text == "MODEL_PHOTO":
                self.set_waifu2x_vulkan_model(waifu2x_vulkan.MODEL_PHOTO_NOISE1)
        elif self.chosen_options.waifu2x_vulkan_model_noise_level == 2:
            if text == "MODEL_ANIME_STYLE_ART_RGB":
                self.set_waifu2x_vulkan_model(waifu2x_vulkan.MODEL_ANIME_STYLE_ART_RGB_NOISE2)
            elif text == "MODEL_CUNET":
                self.set_waifu2x_vulkan_model(waifu2x_vulkan.MODEL_CUNET_NOISE2)
            elif text == "MODEL_CUNET_NO_SCALE":
                self.set_waifu2x_vulkan_model(waifu2x_vulkan.MODEL_CUNET_NO_SCALE_NOISE2)
            elif text == "MODEL_PHOTO":
                self.set_waifu2x_vulkan_model(waifu2x_vulkan.MODEL_PHOTO_NOISE2)
        elif self.chosen_options.waifu2x_vulkan_model_noise_level == 3:
            if text == "MODEL_ANIME_STYLE_ART_RGB":
                self.set_waifu2x_vulkan_model(waifu2x_vulkan.MODEL_ANIME_STYLE_ART_RGB_NOISE3)
            elif text == "MODEL_CUNET":
                self.set_waifu2x_vulkan_model(waifu2x_vulkan.MODEL_CUNET_NOISE3)
            elif text == "MODEL_CUNET_NO_SCALE":
                self.set_waifu2x_vulkan_model(waifu2x_vulkan.MODEL_CUNET_NO_SCALE_NOISE3)
            elif text == "MODEL_PHOTO":
                self.set_waifu2x_vulkan_model(waifu2x_vulkan.MODEL_PHOTO_NOISE3)

    def upscale_factor_spinner_text_changed(self, spinner, text):
        self.set_waifu2x_vulkan_scale_factor(int(text))

    # sets the noise level used by waifu2x_vulkan, and validates the input with the available noise levels
    def set_waifu2x_vulkan_noise_level(self, noise_level):
        if noise_level in range(1, 4):
            self.chosen_options.waifu2x_vulkan_model_noise_level = noise_level
        else:
            log.error(f"Settings: {noise_level} is not a valid noise level")
            self.has_error = True

    # sets the model used by waifu2x_vulkan, and validates the input with the available models
    def set_waifu2x_vulkan_model(self, model):
        if self.chosen_options.waifu2x_vulkan_model_noise_level == 1:
            if model in self.chosen_options.waifu2x_vulkan_model_noise_level_1:
                self.chosen_options.chosen_waifu2x_vulkan_model = model
            else:
                log.error(f"Settings: {model} is not a valid model")
                self.has_error = True
        elif self.chosen_options.waifu2x_vulkan_model_noise_level == 2:
            if model in self.chosen_options.waifu2x_vulkan_model_noise_level_2:
                self.chosen_options.chosen_waifu2x_vulkan_model = model
            else:
                log.error(f"Settings: {model} is not a valid model")
                self.has_error = True
        elif self.chosen_options.waifu2x_vulkan_model_noise_level == 3:
            if model in self.chosen_options.waifu2x_vulkan_model_noise_level_3:
                self.chosen_options.chosen_waifu2x_vulkan_model = model
            else:
                log.error(f"Settings: {model} is not a valid model")
                self.has_error = True
        else:
            log.error(f"Settings: {self.chosen_options.waifu2x_vulkan_model_noise_level} is not a valid noise level")
            self.has_error = True

    # sets the scale factor used by waifu2x_vulkan
    def set_waifu2x_vulkan_scale_factor(self, scale_factor):
        if scale_factor <= 4 and scale_factor >= 2:
            self.chosen_options.chosen_waifu2x_vulkan_scale_factor = scale_factor
        else:
            log.error(f"Settings: {scale_factor} is not a valid scale factor, must be between 2 and 4")
            self.has_error = True
    
    # set the game base directory and validate the existence of the Data folder
    def set_game_base_dir(self, game_base_dir):
        if os.path.exists(game_base_dir + "/Data"):
            self.chosen_options.game_base_dir = game_base_dir
        else:
            log.error(f"Settings: {game_base_dir} is not a valid game base directory")
            self.has_error = True

    # set the quickbms executable and validate the existence of the file
    def set_quickbms_executable(self, quickbms_executable):
        if os.path.exists(quickbms_executable):
            self.chosen_options.quickbms_executable = quickbms_executable
        else:
            log.error(f"Settings: {quickbms_executable} is not a valid quickbms executable")
            self.has_error = True

    # checkbox callback to add or remove the map dat file from the chosen dat files
    def set_map_dat(self):
        if self.ids.map_dat_checkbox.active:
            self.chosen_options.dat_files_chosen.append("map.dat")
        else:
            self.chosen_options.dat_files_chosen.remove("map.dat")
    
    # checkbox callback to add or remove the model dat file from the chosen dat files
    def set_model_dat(self):
        if self.ids.model_dat_checkbox.active:
            self.chosen_options.dat_files_chosen.append("model.dat")
        else:
            self.chosen_options.dat_files_chosen.remove("model.dat")

    # checkbox callback to add or remove the effect dat file from the chosen dat files
    def set_effect_dat(self):
        if self.ids.effect_dat_checkbox.active:
            self.chosen_options.dat_files_chosen.append("effect.dat")
        else:
            self.chosen_options.dat_files_chosen.remove("effect.dat")
    
    # checkbox callback to add or remove the weapon dat file from the chosen dat files
    def set_weapon_dat(self):
        if self.ids.weapon_dat_checkbox.active:
            self.chosen_options.dat_files_chosen.append("weapon.dat")
        else:
            self.chosen_options.dat_files_chosen.remove("weapon.dat")

    def confirm(self):
        self.chosen_options.quickbms_executable = self.ids.quickbms_path_textinput.text
        self.chosen_options.game_base_dir = self.ids.game_path_textinput.text
        self.chosen_options.max_resolution = int(self.ids.max_res_spinner.text)

        # check if base game directory exist
        if not os.path.exists(self.chosen_options.game_base_dir):
            log.error(f"Settings: {self.chosen_options.game_base_dir} is not a valid game base directory")
            self.has_error = True
            
            # show error popup
            self.popup = Popup(title="Error", content=Label(text="Game base directory does not exist"), size_hint=(None, None), size=(400, 400))
            self.popup.open()
            return

        self.dismiss()

    def cancel(self):
        self.cancelled = True
        self.dismiss()

class GITSUmainWindow(App):
    progress = 0
    max_progress = 1
    app_running = True
    upscaling_in_progress = False
    progress_info = ""
    chosen_options = options()
    popup = None
    current_image = None
    progress_file = tracked_progress()
    resume = False
    progress_popup = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # set up events
        self.on_stop = self.on_stop_event

        # set up logging
        log.addHandler(console)

        # display logging
        start_thread(self.update_log)

    def on_stop_event(self):
        self.app_running = False
        log.info("Main: Closing GITS:FA upscaling process")

    def start(self):
        log.info("Main: Starting GITS:FA upscaling process")
        self.root.ids.start_button.disabled = True
        self.progress = 0
        
        # check if there is a progress.txt file
        if os.path.exists("progress.txt"):

            # show popup to ask if the user wants to resume the upscaling
            resume_grid = GridLayout(rows=2, cols=1)
            resume_grid.add_widget(Label(text="Resume the upscaling?"))
            button_grid = GridLayout(rows=1, cols=2)
            resume_button = Button(text="Resume")
            resume_button.bind(on_press=self.resume_upscaling)
            cancel_button = Button(text="Cancel")
            cancel_button.bind(on_press=self.cancel_upscaling)
            button_grid.add_widget(resume_button)
            button_grid.add_widget(cancel_button)
            resume_grid.add_widget(button_grid)

            resume_popup = Popup(title="Resume upscaling", content=resume_grid, size_hint=(0.25, 0.5))
            self.progress_popup = resume_popup
            
            resume_popup.open()
        else:
            #show settings popup and retrieve options
            self.popup = SettingsPopup()
            self.popup.bind(on_dismiss=self.settings_popup_callback)
            self.popup.open()

    def resume_upscaling(self, button):
        self.progress_popup.dismiss()
        self.progress_file.load_from_file("progress.txt")
        self.resume = True

        # set the options from the progress.txt file
        self.chosen_options = self.progress_file.chosen_options
        start_thread(self.update_progress)
        start_thread(self.start_process)

    def cancel_upscaling(self, button):
        self.progress_popup.dismiss()

        #show settings popup and retrieve options
        self.popup = SettingsPopup()
        self.popup.bind(on_dismiss=self.settings_popup_callback)
        self.popup.open()

    def settings_popup_callback(self, popup):
        self.chosen_options = popup.chosen_options
        
        if popup.cancelled:
            self.root.ids.start_button.disabled = False
            log.info("Main: Upscaling cancelled")
        else:
            self.progress_file.chosen_options = self.chosen_options
            start_thread(self.update_progress)
            start_thread(self.start_process)

    # updates the progress bar
    def update_progress(self):
        while self.app_running:
            self.root.ids.progress_bar.max = self.max_progress
            self.root.ids.progress_bar.value = self.progress
            self.root.ids.status_label.text = f"{self.progress}/{int(self.root.ids.progress_bar.max)}"
            self.root.ids.status_label_info.text = self.progress_info
            self.update_current_image()

            time.sleep(0.05)

    @mainthread
    def update_current_image(self):
        # if current image is not None, and file exists, display it
        if self.current_image is not None and os.path.exists(self.current_image):
            self.root.ids.preview_image.source = self.current_image
            self.current_image = None

    # update log_lable with log_stream
    def update_log(self):
        # run while app is not closing
        while self.app_running:
            if self.root is not None:
                content = console.stream.getvalue()
                lines = content.splitlines()
                # display only the last 20 lines
                self.root.ids.log_label.text = str.join("\n", lines[-20:])
            time.sleep(0.5)

    def start_process(self):
        # get game base path
        game_base_path = self.chosen_options.game_base_dir

        # start unpacking and upscaling
        self.unpack_and_upscale(game_base_path)

    def clear_temp_dir(self):
        # clear temp directory
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        os.mkdir(temp_path)

        # if 1.png and 2.png exist, delete them
        if os.path.exists("1.png"):
            os.remove("1.png")
        if os.path.exists("2.png"):
            os.remove("2.png")

    def unpack_and_upscale(self, game_base_path):
        self.upscaling_in_progress = True
        dat_files = self.chosen_options.dat_files_chosen
        data_path = "\\Data\\"
        dds_files = []

        # clear temp directory
        self.clear_temp_dir()

        # prepare progress bar
        self.progress = 0
        self.max_progress = len(dat_files) * 2

        quickbms_available = False
        quickbms_executable = self.chosen_options.quickbms_executable

        # Check if quickbms is available
        if os.path.exists(quickbms_executable):
            quickbms_available = True
            log.info("Main: quickbms is available")
        
        if not self.resume:

            # if quickbms is not available, use unpacker.py which is way slower
            # unpack all the dat files
            if not quickbms_available:
                for dat_file in dat_files:
                    # check if there is no .dat.bak in the game directory
                    if os.path.exists(game_base_path + data_path + dat_file + ".bak"):
                        # if there is a .dat.bak it was already unpacked
                        continue

                    log.info(f"Main: Unpacking {dat_file}")
                    self.progress_info = f"Unpacking {dat_file}"
                    unpack_file(game_base_path + data_path + dat_file, game_base_path + data_path)
                    self.progress += 1
            else:
                # unpack all the dat files with quickbms and subprocess
                for dat_file in dat_files:
                    # check if there is no .dat.bak in the game directory
                    if os.path.exists(game_base_path + data_path + dat_file + ".bak"):
                        # if there is a .dat.bak it was already unpacked
                        log.info(f"Main: {dat_file} was already unpacked")
                        continue

                    log.info(f"Main: Unpacking {dat_file}")
                    self.progress_info = f"Unpacking {dat_file}"
                    subprocess.run([quickbms_executable, "-o", "GSFA.bms", game_base_path + data_path + dat_file, game_base_path + data_path])
                    self.progress += 1

        # collect all the dds files
        for dat_file in dat_files:
            log.info(f"Main: Collecting dds files from {dat_file}")
            self.progress_info = f"Collecting dds files from {dat_file}"
            dds_files += collect_dds_files(game_base_path +
                                           data_path + dat_file[:-4])
            self.progress += 1

        self.progress = 0
        self.max_progress = len(dds_files)

        # Method 1: Init tf for better memory management
        if self.chosen_options.chosen_upscale_method == "ESRGAN_4x":
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                try:
                    # Currently, memory growth needs to be the same across GPUs
                    for gpu in gpus:
                        tf.config.experimental.set_memory_growth(gpu, True)
                    logical_gpus = tf.config.list_logical_devices('GPU')
                except RuntimeError as e:
                    # Memory growth must be set before GPUs have been initialized
                    log.error(e)

            model = tf.saved_model.load(working_dir)
        else:
            # Method 3: Init waifu2x_vulkan
            sts = waifu2x_vulkan.init()
            
            isCpuModel = False
            if sts < 0:
                # cpu model
                isCpuModel = True
                
            # get gpu list
            infos = waifu2x_vulkan.getGpuInfo()
            
            # if llvm gpu, use cpu model
            if infos and len(infos) == 1 and "LLVM" in infos[0]:
                isCpuModel = True
                
            cpuNum = waifu2x_vulkan.getCpuCoreNum()
            gpuNum = waifu2x_vulkan.getGpuCoreNum(0)
            log.info("init, code:{}, gpuList:{}, cpuNum:{}, gpuNum:{}".format(str(sts), infos, cpuNum, gpuNum))    

            # select gpu, if cpu model set cpu num
            if isCpuModel:
                sts = waifu2x_vulkan.initSet(-1, cpuNum)
            else:
                sts = waifu2x_vulkan.initSet(0)

            log.info("init set, code:{}".format(str(sts)))


        # upscale all the dds files
        for dds_file in dds_files:
            try:
                # skip if file is already upscaled and resume is enabled
                if self.resume and self.progress_file.file_id > dds_files.index(dds_file):
                    log.info(f"Main: Skipping {dds_file} with id {dds_files.index(dds_file)}")
                    self.progress += 1
                    continue

                # set progress_file attributes
                self.progress_file.file_id = dds_files.index(dds_file)

                # write progress to file
                self.progress_file.save_to_file("progress.txt")

                dds_filename = os.path.basename(dds_file)

                # dds to png
                log.info(f"Main: Converting {dds_filename} to png")
                self.progress_info = f"Converting {dds_filename} to png"
                compression = dds_to_png(dds_file, temp_path + dds_filename[:-4] + ".png")
                
                # set source of preview image
                self.current_image = temp_path + dds_filename[:-4] + ".png"

                # create alpha mask
                log.info(f"Main: Creating alpha mask for {dds_filename}")
                self.progress_info = f"Creating alpha mask for {dds_filename}"
                generate_alphamask(
                    temp_path + dds_filename[:-4] + ".png", temp_path + "alphamask.png")
                remove_alpha_channel(
                    temp_path + dds_filename[:-4] + ".png", temp_path + "noalpha.png")
                os.unlink(temp_path + dds_filename[:-4] + ".png")

                # upscale the mask and the image with the removed alpha channel
                log.info(f"Main: Upscaling {dds_filename}")
                self.progress_info = f"Upscaling {dds_filename}"


                if self.chosen_options.chosen_upscale_method == "ESRGAN_4x":
                    # Method 1: Upscale with tensorflow in this process

                    alphamask_upscaled = upscale_image(model, temp_path + "\\alphamask.png")
                    no_alpha_upscaled = upscale_image(model, temp_path + "\\noalpha.png")
                    save_image(alphamask_upscaled, temp_path + "\\alphamask_upscaled")
                    save_image(no_alpha_upscaled, temp_path + "\\noalpha_upscaled")

                    # convert the upscaled jpgs to pngs
                    log.info(f"Main: Converting upscaled images to png")
                    self.progress_info = f"Converting upscaled images to png"
                    jpg_to_png(temp_path + "alphamask_upscaled.jpg", temp_path + "alphamask_upscaled.png")
                    jpg_to_png(temp_path + "noalpha_upscaled.jpg", temp_path + "noalpha_upscaled.png")

                    # Method 2: Upscale with tensorflow in a subprocess (not used anymore)

                    # use subprocess to run the upscaling script
                    # images_to_upscale = [working_dir + "\\" + temp_path + "\\alphamask.png", working_dir + "\\" + temp_path + "\\noalpha.png"]

                    # subprocess.run(["python", "upscaler.py", "-i" + str.join(',', images_to_upscale),
                    #                "-m" + working_dir], cwd=working_dir)

                if self.chosen_options.chosen_upscale_method == "waifu2x_vulkan":

                    # Method 3: Upscale with waifu2x-vulkan     
                    alphamask = open(temp_path + "alphamask.png", "rb").read()
                    noalpha = open(temp_path + "noalpha.png", "rb").read()

                    backId = 1
                    count = 0

                    if waifu2x_vulkan.add(alphamask, self.chosen_options.chosen_waifu2x_vulkan_model, backId, self.chosen_options.upscale_factor) > 0:
                        count += 1
                    
                    backId = 2
                    if waifu2x_vulkan.add(noalpha, self.chosen_options.chosen_waifu2x_vulkan_model, backId, self.chosen_options.upscale_factor) > 0:
                        count += 1
                    
                    while count > 0:
                        time.sleep(1)
                        # block
                        info = waifu2x_vulkan.load(0)
                        if not info:
                            break 
                        count -= 1
                        newData, format, backId, tick = info
                        f = open(str(backId) + "." + format, "wb+")
                        f.write(newData)
                        f.close()

                    # rename the upscaled images
                    os.rename("1.png", temp_path + "alphamask_upscaled.png")
                    os.rename("2.png", temp_path + "noalpha_upscaled.png")

                # apply the mask to the upscaled image
                log.info(f"Main: Applying alpha mask to {dds_filename}")
                self.progress_info = f"Applying alpha mask to {dds_filename}"
                apply_alphamask(temp_path + "noalpha_upscaled.png", temp_path +
                                "\\alphamask_upscaled.png", temp_path + "upscaled.png")

                # downscale the upscaled image if the resolution is too high
                # check if image size is larger than options.max_resolution
                image = Image.open(temp_path + "upscaled.png")
                if image.size[0] > self.chosen_options.max_resolution or image.size[1] > self.chosen_options.max_resolution:
                    image.close()
                    log.info(f"Main: Downscaling {dds_filename}")
                    self.progress_info = f"Downscaling {dds_filename}"
                    downscale_image(temp_path + "upscaled.png", self.chosen_options.max_resolution)
                else:
                    image.close()


                # create dds file from upscaled image
                log.info(f"Main: Creating dds file from upscaled image")
                self.progress_info = f"Creating dds file from upscaled image"
                png_to_dds(temp_path + "\\upscaled.png",
                        temp_path + "\\upscaled.dds", compression)

                # replace the old dds file with the new one
                log.info(f"Main: Replacing {dds_filename} with upscaled dds file")
                self.progress_info = f"Replacing {dds_filename} with upscaled dds file"
                os.unlink(dds_file)
                # copy file to original location
                shutil.copy(temp_path + "\\upscaled.dds", dds_file)

                # delete temp files
                log.info(f"Main: Deleting temp files")
                self.progress_info = f"Deleting temp files"
                os.unlink(temp_path + "\\alphamask.png")
                os.unlink(temp_path + "\\noalpha.png")
                os.unlink(temp_path + "\\alphamask_upscaled.png")
                os.unlink(temp_path + "\\noalpha_upscaled.png")
                os.unlink(temp_path + "\\upscaled.png")
                os.unlink(temp_path + "\\upscaled.dds")
            except:
                log.exception(f"Main: Error while processing file {dds_filename}")
                self.progress_info = f"Error while processing file {dds_filename}"

            self.progress += 1
        
        # rename orginal .dat files to .dat.bak
        for dat_file in dat_files:
            # check if file exists
            if os.path.exists(dat_file):
                os.rename(dat_file, dat_file + ".bak")

        # delete progress.txt and options.txt
        if os.path.exists("progress.txt"):
            os.unlink("progress.txt")
        if os.path.exists("options.txt"):
            os.unlink("options.txt")

        # show success popup
        log.info(f"Main: Finished processing {len(dds_files)} dds files")
        self.progress_info = f"Finished processing {len(dds_files)} dds files"
        success_popup = Popup(title="Success", content=Label(text="Finished processing files"), size_hint=(0.25, 0.5), auto_dismiss=False)
        success_popup.open()


if __name__ == '__main__':
    mainWindow = GITSUmainWindow()
    mainWindow.run()
