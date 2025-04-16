import os
import random
import sys
from typing import Sequence, Mapping, Any, Union
import torch


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
    comfyui_path = find_path("ComfyUI")
    if comfyui_path is not None and os.path.isdir(comfyui_path):
        sys.path.append(comfyui_path)
        print(f"'{comfyui_path}' added to sys.path")


def add_extra_model_paths() -> None:
    """
    Parse the optional extra_model_paths.yaml file and add the parsed paths to the sys.path.
    """
    try:
        from main import load_extra_path_config
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
    VAELoader,
    ControlNetLoader,
    ControlNetApplyAdvanced,
    LoadImage,
    NODE_CLASS_MAPPINGS,
    UNETLoader,
    CLIPTextEncode,
    VAEEncode,
    SaveImage,
    VAEDecode,
    DualCLIPLoader,
)


def main():
    import_custom_nodes()
    with torch.inference_mode():
        dualcliploader = DualCLIPLoader()
        dualcliploader_94 = dualcliploader.load_clip(
            clip_name1="t5xxl_fp16.safetensors",
            clip_name2="clip_l.safetensors",
            type="flux",
            device="default",
        )

        cliptextencode = CLIPTextEncode()
        cliptextencode_23 = cliptextencode.encode(
            text="", clip=get_value_at_index(dualcliploader_94, 0)
        )

        loadimage = LoadImage()
        loadimage_24 = loadimage.load_image(image="elon (1).jpg")

        loadimage_40 = loadimage.load_image(image="chatgpt_elon.png")

        vaeloader = VAELoader()
        vaeloader_95 = vaeloader.load_vae(vae_name="FLUX1/ae.safetensors")

        vaeencode = VAEEncode()
        vaeencode_35 = vaeencode.encode(
            pixels=get_value_at_index(loadimage_40, 0),
            vae=get_value_at_index(vaeloader_95, 0),
        )

        randomnoise = NODE_CLASS_MAPPINGS["RandomNoise"]()
        randomnoise_39 = randomnoise.get_noise(noise_seed=random.randint(1, 2**64))

        cliptextencode_42 = cliptextencode.encode(
            text="", clip=get_value_at_index(dualcliploader_94, 0)
        )

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

        ksamplerselect = NODE_CLASS_MAPPINGS["KSamplerSelect"]()
        ksamplerselect_50 = ksamplerselect.get_sampler(sampler_name="euler")

        unetloader = UNETLoader()
        unetloader_93 = unetloader.load_unet(
            unet_name="flux1-dev.safetensors", weight_dtype="default"
        )

        faceanalysismodels = NODE_CLASS_MAPPINGS["FaceAnalysisModels"]()
        faceanalysismodels_118 = faceanalysismodels.load_models(
            library="insightface", provider="CUDA"
        )

        applypulidflux = NODE_CLASS_MAPPINGS["ApplyPulidFlux"]()
        setunioncontrolnettype = NODE_CLASS_MAPPINGS["SetUnionControlNetType"]()
        controlnetapplyadvanced = ControlNetApplyAdvanced()
        basicguider = NODE_CLASS_MAPPINGS["BasicGuider"]()
        basicscheduler = NODE_CLASS_MAPPINGS["BasicScheduler"]()
        samplercustomadvanced = NODE_CLASS_MAPPINGS["SamplerCustomAdvanced"]()
        vaedecode = VAEDecode()
        faceembeddistance = NODE_CLASS_MAPPINGS["FaceEmbedDistance"]()
        display_any_rgthree = NODE_CLASS_MAPPINGS["Display Any (rgthree)"]()
        image_comparer_rgthree = NODE_CLASS_MAPPINGS["Image Comparer (rgthree)"]()
        saveimage = SaveImage()

        for q in range(10):
            applypulidflux_31 = applypulidflux.apply_pulid_flux(
                weight=0.75,
                start_at=0.1,
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
                unique_id=17601617597548643515,
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
                model=get_value_at_index(applypulidflux_31, 0),
                conditioning=get_value_at_index(controlnetapplyadvanced_37, 0),
            )

            basicscheduler_131 = basicscheduler.get_sigmas(
                scheduler="beta",
                steps=28,
                denoise=0.75,
                model=get_value_at_index(applypulidflux_31, 0),
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

            faceembeddistance_117 = faceembeddistance.analize(
                similarity_metric="cosine",
                filter_thresh=100,
                filter_best=0,
                generate_image_overlay=True,
                analysis_models=get_value_at_index(faceanalysismodels_118, 0),
                reference=get_value_at_index(loadimage_24, 0),
                image=get_value_at_index(vaedecode_114, 0),
            )

            display_any_rgthree_121 = display_any_rgthree.main(
                source=get_value_at_index(faceembeddistance_117, 1)
            )

            image_comparer_rgthree_123 = image_comparer_rgthree.compare_images(
                image_a=get_value_at_index(loadimage_40, 0),
                image_b=get_value_at_index(vaedecode_114, 0),
            )

            saveimage_128 = saveimage.save_images(
                filename_prefix="FaceEnhanced",
                images=get_value_at_index(vaedecode_114, 0),
            )

            saveimage_129 = saveimage.save_images(
                filename_prefix="FaceEmbedDist",
                images=get_value_at_index(faceembeddistance_117, 0),
            )


if __name__ == "__main__":
    main()
