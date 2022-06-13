from MODELS.orchestra_main_model_two import main_orchestrator_model
from UTILS.base64_encode_decode import image_to_base64

input_image = r'C:\Users\Emerson\Desktop\brainIAcs\MASSA_IMAGENS\RG\Jose_Clerton.png'

input = {
    "tipo_documento": "RG",
    "verso": True,
    "imagem": image_to_base64(input_image)
}

result_image = main_orchestrator_model(input)

print(result_image)