import os
import random
import sys
from typing import Sequence, Mapping, Any, Union
import torch
# import spaces
COMFYUI_PATH = "./ComfyUI"

"""
To avoid loading the models each time, we store them in a global variable.
"""
COMFY_MODELS = None

def get_value_at_index(obj: Union[Sequence, Mapping], index: int) -> Any:
    """Returns the value at the given index of a sequence or mapping.

    If the object is a sequence (like list or string), returns the value at the given index.
    If the object is a mapping (like a dictionary), returns the value at the index-th key.

    Some return a dictionary, in these cases, we look for the "results" key

    Args:
        obj (Union[Sequence, Mapping]): The object to retrieve the value from.
        index (int): The index of the value to retrieve.

    Returns:
        Any: The value at the given index.

    Raises:
        IndexError: If the index is out of bounds for the object and the object is not a mapping.
    """
    try:
        return obj[index]
    except KeyError:
        return obj["result"][index]


def find_path(name: str, path: str = None) -> str:
    """
    Recursively looks at parent folders starting from the given path until it finds the given name.
    Returns the path as a Path object if found, or None otherwise.
    """
    # If no path is given, use the current working directory
    if path is None:
        path = os.getcwd()

    # Check if the current directory contains the name
    if name in os.listdir(path):
        path_name = os.path.join(path, name)
        print(f"{name} found: {path_name}")
        return path_name

    # Get the parent directory
    parent_directory = os.path.dirname(path)

    # If the parent directory is the same as the current directory, we've reached the root and stop the search
    if parent_directory == path:
        return None

    # Recursively call the function with the parent directory
    return find_path(name, parent_directory)


def add_comfyui_directory_to_sys_path() -> None:
    """
    Add 'ComfyUI' to the sys.path
    """
    sys.path.append(COMFYUI_PATH)


def add_extra_model_paths() -> None:
    """
    Parse the optional extra_model_paths.yaml file and add the parsed paths to the sys.path.
    """
    try:
        from test import load_extra_path_config
    except ImportError:
        print(
            "Could not import load_extra_path_config from main.py. Looking in utils.extra_config instead."
        )
        from utils.extra_config import load_extra_path_config

    extra_model_paths = find_path("extra_model_paths.yaml")

    if extra_model_paths is not None:
        load_extra_path_config(extra_model_paths)
    else:
        print("Could not find the extra_model_paths config file.")


add_comfyui_directory_to_sys_path()
add_extra_model_paths()


def import_custom_nodes() -> None:
    """Find all custom nodes in the custom_nodes folder and add those node objects to NODE_CLASS_MAPPINGS

    This function sets up a new asyncio event loop, initializes the PromptServer,
    creates a PromptQueue, and initializes the custom nodes.
    """
    import asyncio
    import execution
    from nodes import init_extra_nodes
    import server

    # Creating a new event loop and setting it as the default loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Creating an instance of PromptServer with the loop
    server_instance = server.PromptServer(loop)
    execution.PromptQueue(server_instance)

    # Initializing custom nodes
    init_extra_nodes()


from nodes import (
    LoadImage,
    SaveImage,
    NODE_CLASS_MAPPINGS,
    CLIPTextEncode,
    VAELoader,
    VAEEncode,
    DualCLIPLoader,
    VAEDecode,
    UNETLoader,
    ControlNetLoader,
    ControlNetApplyAdvanced,
)

@torch.inference_mode()
def load_models():
    dualcliploader = DualCLIPLoader()
    dualcliploader_94 = dualcliploader.load_clip(
        clip_name1="t5xxl_fp16.safetensors",
        clip_name2="clip_l.safetensors",
        type="flux",
        device="default",
    )

    vaeloader = VAELoader()
    vaeloader_95 = vaeloader.load_vae(vae_name="ae.safetensors")

    pulidfluxmodelloader = NODE_CLASS_MAPPINGS["PulidFluxModelLoader"]()
    pulidfluxmodelloader_44 = pulidfluxmodelloader.load_model(
        pulid_file="pulid_flux_v0.9.1.safetensors"
    )

    pulidfluxevacliploader = NODE_CLASS_MAPPINGS["PulidFluxEvaClipLoader"]()
    pulidfluxevacliploader_45 = pulidfluxevacliploader.load_eva_clip()

    pulidfluxinsightfaceloader = NODE_CLASS_MAPPINGS["PulidFluxInsightFaceLoader"]()
    pulidfluxinsightfaceloader_46 = pulidfluxinsightfaceloader.load_insightface(
        provider="CUDA"
    )

    controlnetloader = ControlNetLoader()
    controlnetloader_49 = controlnetloader.load_controlnet(
        control_net_name="Flux_Dev_ControlNet_Union_Pro_ShakkerLabs.safetensors"
    )

    unetloader = UNETLoader()
    unetloader_93 = unetloader.load_unet(
        unet_name="flux1-dev.safetensors", weight_dtype="default"
    )

    return {
        "dualcliploader_94": dualcliploader_94,
        "vaeloader_95": vaeloader_95,
        "pulidfluxmodelloader_44": pulidfluxmodelloader_44,
        "pulidfluxevacliploader_45": pulidfluxevacliploader_45,
        "pulidfluxinsightfaceloader_46": pulidfluxinsightfaceloader_46,
        "controlnetloader_49": controlnetloader_49,
        "unetloader_93": unetloader_93
    }

def initialize_models():
    global COMFY_MODELS
    if COMFY_MODELS is None:
        import_custom_nodes()  # Ensure NODE_CLASS_MAPPINGS is initialized
        COMFY_MODELS = load_models()

initialize_models()

def main(
    face_image: str,
    input_image: str,
    output_image: str,
    dist_image: str = None,
    positive_prompt: str = "",
    id_weight: float = 0.75,
):
    global COMFY_MODELS
    if COMFY_MODELS is None:
        raise ValueError("Models must be initialized before calling main(). Call initialize_models() first.")
    with torch.inference_mode():
        dualcliploader_94 = COMFY_MODELS["dualcliploader_94"]
        vaeloader_95 = COMFY_MODELS["vaeloader_95"]
        pulidfluxmodelloader_44 = COMFY_MODELS["pulidfluxmodelloader_44"]
        pulidfluxevacliploader_45 = COMFY_MODELS["pulidfluxevacliploader_45"]
        pulidfluxinsightfaceloader_46 = COMFY_MODELS["pulidfluxinsightfaceloader_46"]
        controlnetloader_49 = COMFY_MODELS["controlnetloader_49"]
        unetloader_93 = COMFY_MODELS["unetloader_93"]

        cliptextencode = CLIPTextEncode()
        cliptextencode_23 = cliptextencode.encode(
            text="", clip=get_value_at_index(dualcliploader_94, 0)
        )

        loadimage = LoadImage()
        loadimage_24 = loadimage.load_image(image=face_image)

        loadimage_40 = loadimage.load_image(image=input_image)

        vaeencode = VAEEncode()
        vaeencode_35 = vaeencode.encode(
            pixels=get_value_at_index(loadimage_40, 0),
            vae=get_value_at_index(vaeloader_95, 0),
        )

        randomnoise = NODE_CLASS_MAPPINGS["RandomNoise"]()
        randomnoise_39 = randomnoise.get_noise(noise_seed=random.randint(1, 2**64))

        cliptextencode_42 = cliptextencode.encode(
            text=positive_prompt, clip=get_value_at_index(dualcliploader_94, 0)
        )

        ksamplerselect = NODE_CLASS_MAPPINGS["KSamplerSelect"]()
        ksamplerselect_50 = ksamplerselect.get_sampler(sampler_name="euler")

        applypulidflux = NODE_CLASS_MAPPINGS["ApplyPulidFlux"]()
        setunioncontrolnettype = NODE_CLASS_MAPPINGS["SetUnionControlNetType"]()
        controlnetapplyadvanced = ControlNetApplyAdvanced()
        basicguider = NODE_CLASS_MAPPINGS["BasicGuider"]()
        basicscheduler = NODE_CLASS_MAPPINGS["BasicScheduler"]()
        samplercustomadvanced = NODE_CLASS_MAPPINGS["SamplerCustomAdvanced"]()
        vaedecode = VAEDecode()

        applypulidflux_133 = applypulidflux.apply_pulid_flux(
            weight=id_weight,
            start_at=0.10000000000000002,
            end_at=1,
            fusion="mean",
            fusion_weight_max=1,
            fusion_weight_min=0,
            train_step=1000,
            use_gray=True,
            model=get_value_at_index(unetloader_93, 0),
            pulid_flux=get_value_at_index(pulidfluxmodelloader_44, 0),
            eva_clip=get_value_at_index(pulidfluxevacliploader_45, 0),
            face_analysis=get_value_at_index(pulidfluxinsightfaceloader_46, 0),
            image=get_value_at_index(loadimage_24, 0),
            unique_id=1674270197144619516,
        )

        setunioncontrolnettype_41 = setunioncontrolnettype.set_controlnet_type(
            type="tile", control_net=get_value_at_index(controlnetloader_49, 0)
        )

        controlnetapplyadvanced_37 = controlnetapplyadvanced.apply_controlnet(
            strength=1,
            start_percent=0.1,
            end_percent=0.8,
            positive=get_value_at_index(cliptextencode_42, 0),
            negative=get_value_at_index(cliptextencode_23, 0),
            control_net=get_value_at_index(setunioncontrolnettype_41, 0),
            image=get_value_at_index(loadimage_40, 0),
            vae=get_value_at_index(vaeloader_95, 0),
        )

        basicguider_122 = basicguider.get_guider(
            model=get_value_at_index(applypulidflux_133, 0),
            conditioning=get_value_at_index(controlnetapplyadvanced_37, 0),
        )

        basicscheduler_131 = basicscheduler.get_sigmas(
            scheduler="beta",
            steps=28,
            denoise=0.75,
            model=get_value_at_index(applypulidflux_133, 0),
        )

        samplercustomadvanced_1 = samplercustomadvanced.sample(
            noise=get_value_at_index(randomnoise_39, 0),
            guider=get_value_at_index(basicguider_122, 0),
            sampler=get_value_at_index(ksamplerselect_50, 0),
            sigmas=get_value_at_index(basicscheduler_131, 0),
            latent_image=get_value_at_index(vaeencode_35, 0),
        )

        vaedecode_114 = vaedecode.decode(
            samples=get_value_at_index(samplercustomadvanced_1, 0),
            vae=get_value_at_index(vaeloader_95, 0),
        )

        save_comfy_images(get_value_at_index(vaedecode_114, 0), [output_image])


def save_comfy_images(images, output_dirs):
    # images is a PyTorch tensor with shape [batch_size, height, width, channels]
    import numpy as np
    from PIL import Image
    
    for idx, image in enumerate(images):
        # Create the output directory if it doesn't exist
        output_dir = os.path.dirname(output_dirs[idx])
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        numpy_image = 255. * image.cpu().numpy()
        numpy_image = np.clip(numpy_image, 0, 255).astype(np.uint8)
        pil_image = Image.fromarray(numpy_image)
        pil_image.save(output_dirs[idx])

# @spaces.GPU
def face_enhance(face_image: str, input_image: str, output_image: str, dist_image: str = None, positive_prompt: str = "", id_weight: float = 0.75):
    initialize_models()  # Ensure models are loaded
    main(face_image, input_image, output_image, dist_image, positive_prompt, id_weight)

if __name__ == "__main__":
    pass
