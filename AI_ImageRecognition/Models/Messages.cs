using AI_ImageRacognition.Utilities;
using Microsoft.Extensions.AI;

namespace AI_ImageRacognition.Models;

public record Messages(string ModelName,
                       List<ChatPrompt> Prompts);

public record ChatPrompt(ChatRole Role,
                         string DefaultPrompt,
                         List<string>? Contents,
                         List<Image>? Images);

public record Image(string ImageData,
                    string MediaType);