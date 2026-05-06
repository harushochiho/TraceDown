using AI_ImageRacognition.Utilities;
using Microsoft.Extensions.AI;

namespace AI_ImageRacognition.Models;

public record Messages
{
    public string           ModelName = string.Empty;
    public List<ChatPrompt> Prompts   = [];
}

public record ChatPrompt
{
    public ChatRole Role;

    public string DefaultPrompt = string.Empty;
    
    public List<string> Contents = [];

    public List<Image> Images = [];
    
}

public record Image
{
    public string ImageData = string.Empty;

    public string MediaType = "image/png";
}