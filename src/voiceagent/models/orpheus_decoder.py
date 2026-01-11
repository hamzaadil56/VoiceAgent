"""
Orpheus TTS decoder using SNAC (Self-supervised Neural Audio Codec).

Based on: https://github.com/isaiahbjork/orpheus-tts-local
"""

from snac import SNAC
import numpy as np
import torch
from rich.console import Console

console = Console()

# Load SNAC model
console.print("[cyan]Loading SNAC decoder model...[/cyan]")
snac_model = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").eval()

# Check device availability
snac_device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
console.print(f"[green]✓ SNAC decoder loaded on device: {snac_device}[/green]")
snac_model = snac_model.to(snac_device)


def convert_to_audio(multiframe, count):
    """
    Convert token frames to audio using SNAC decoder.
    
    Args:
        multiframe: List of audio tokens
        count: Current token count
        
    Returns:
        Audio bytes in PCM format, or None if error
    """
    if len(multiframe) < 7:
        return None
    
    codes_0 = torch.tensor([], device=snac_device, dtype=torch.int32)
    codes_1 = torch.tensor([], device=snac_device, dtype=torch.int32)
    codes_2 = torch.tensor([], device=snac_device, dtype=torch.int32)

    num_frames = len(multiframe) // 7
    frame = multiframe[:num_frames*7]

    for j in range(num_frames):
        i = 7*j
        if codes_0.shape[0] == 0:
            codes_0 = torch.tensor([frame[i]], device=snac_device, dtype=torch.int32)
        else:
            codes_0 = torch.cat([codes_0, torch.tensor([frame[i]], device=snac_device, dtype=torch.int32)])

        if codes_1.shape[0] == 0:
            codes_1 = torch.tensor([frame[i+1]], device=snac_device, dtype=torch.int32)
            codes_1 = torch.cat([codes_1, torch.tensor([frame[i+4]], device=snac_device, dtype=torch.int32)])
        else:
            codes_1 = torch.cat([codes_1, torch.tensor([frame[i+1]], device=snac_device, dtype=torch.int32)])
            codes_1 = torch.cat([codes_1, torch.tensor([frame[i+4]], device=snac_device, dtype=torch.int32)])
        
        if codes_2.shape[0] == 0:
            codes_2 = torch.tensor([frame[i+2]], device=snac_device, dtype=torch.int32)
            codes_2 = torch.cat([codes_2, torch.tensor([frame[i+3]], device=snac_device, dtype=torch.int32)])
            codes_2 = torch.cat([codes_2, torch.tensor([frame[i+5]], device=snac_device, dtype=torch.int32)])
            codes_2 = torch.cat([codes_2, torch.tensor([frame[i+6]], device=snac_device, dtype=torch.int32)])
        else:
            codes_2 = torch.cat([codes_2, torch.tensor([frame[i+2]], device=snac_device, dtype=torch.int32)])
            codes_2 = torch.cat([codes_2, torch.tensor([frame[i+3]], device=snac_device, dtype=torch.int32)])
            codes_2 = torch.cat([codes_2, torch.tensor([frame[i+5]], device=snac_device, dtype=torch.int32)])
            codes_2 = torch.cat([codes_2, torch.tensor([frame[i+6]], device=snac_device, dtype=torch.int32)])

    codes = [codes_0.unsqueeze(0), codes_1.unsqueeze(0), codes_2.unsqueeze(0)]
    
    # Validate all tokens are between 0 and 4096
    if torch.any(codes[0] < 0) or torch.any(codes[0] > 4096) or \
       torch.any(codes[1] < 0) or torch.any(codes[1] > 4096) or \
       torch.any(codes[2] < 0) or torch.any(codes[2] > 4096):
        return None

    with torch.inference_mode():
        audio_hat = snac_model.decode(codes)
    
    audio_slice = audio_hat[:, :, 2048:4096]
    detached_audio = audio_slice.detach().cpu()
    audio_np = detached_audio.numpy()
    audio_int16 = (audio_np * 32767).astype(np.int16)
    audio_bytes = audio_int16.tobytes()
    return audio_bytes


def turn_token_into_id(token_string, index):
    """
    Convert custom_token string to numeric ID for SNAC processing.
    
    Args:
        token_string: String like "<custom_token_12345>"
        index: Current token index
        
    Returns:
        Converted token ID or None if invalid
    """
    token_string = token_string.strip()
    
    # Find the last token in the string
    last_token_start = token_string.rfind("<custom_token_")
    
    if last_token_start == -1:
        return None
    
    # Extract the last token
    last_token = token_string[last_token_start:]
    
    # Process the last token
    if last_token.startswith("<custom_token_") and last_token.endswith(">"):
        try:
            number_str = last_token[14:-1]
            return int(number_str) - 10 - ((index % 7) * 4096)
        except ValueError:
            return None
    else:
        return None

