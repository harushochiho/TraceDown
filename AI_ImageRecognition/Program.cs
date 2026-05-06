using System.Diagnostics;
using System.Text;
using System.Text.Json;
using AI_ImageRacognition;
using AI_ImageRacognition.Models;
using AI_ImageRacognition.Utilities;
using Microsoft.Extensions.AI;
using OllamaSharp;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();
builder.Services.AddKeyedChatClient("deepseek",
                                    new OllamaApiClient(new HttpClient { BaseAddress = new Uri("http://localhost:8833/"), Timeout = Timeout.InfiniteTimeSpan },
                                                        "deepseek-ocr:latest"));
builder.Services.AddKeyedChatClient("llama",
                                    new OllamaApiClient(new HttpClient { BaseAddress = new Uri("http://localhost:8833/"), Timeout = Timeout.InfiniteTimeSpan },
                                                        "llama3.2-vision:latest"));
var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseHttpsRedirection();

app.MapGet("/aicalling",
           async () =>
           {
               var deepseekChatClient = app.Services.GetKeyedService<IChatClient>("deepseek");
               var llamaChatClient = app.Services.GetKeyedService<IChatClient>("llama");
               var deepseekPrompt = File.ReadAllText("deepseek_prompt.txt",
                                                     Encoding.UTF8);
               var llamaPrompt = File.ReadAllText("llama_prompt.txt",
                                                  Encoding.UTF8);
               var systemPrompt = File.ReadAllText("system_prompt.txt",
                                                   Encoding.UTF8);
               Debug.Print($"Deepseek prompt: \n{deepseekPrompt}\n");
               Debug.Print($"Llama prompt: \n{llamaPrompt}\n");
               Debug.Print($"System prompt: \n{systemPrompt}\n");
               // var message = new ChatMessage(ChatRole.User,
               //                               """Extract all line items from this receipt. Respond in JSON format with this structure:{'CompanyName':'Company Name','items': [{ 'name': 'English item name(Chinese item name)', 'quantity': 1.500, 'unitPrice': 0.00, 'totalPrice': 0.00, 'Category': 'category', 'OnSale':true, 'Taxable':true }],  'subtotal': 0.00 }""");
               var deepseekMessage = new ChatMessage(ChatRole.User,
                                                     deepseekPrompt);
               var llamaMessage = new ChatMessage(ChatRole.User,
                                                  llamaPrompt);
               var systemMessage = new ChatMessage(ChatRole.System,
                                                   systemPrompt);
               byte[] receiptBytes = File.ReadAllBytes("receipt.png");

               deepseekMessage.Contents.Add(new DataContent(receiptBytes,
                                                            "image/png"));

               //var response = await chatClient.GetResponseAsync<Receipt>([systemMessage, message], new ChatOptions{ Temperature = 0});
               var deepseekResponse = await deepseekChatClient.GetResponseAsync([deepseekMessage],
                                                                                new ChatOptions { Temperature = 0 });
               File.AppendAllText("deepseek_response.txt",
                                  JsonSerializer.Serialize(deepseekResponse) + "\n");
               llamaMessage.Contents.Add(new TextContent(deepseekResponse.Text));
               llamaMessage.Contents.Add(new DataContent(receiptBytes,
                                                         "image/png"));
               var llamaResponse = await llamaChatClient.GetResponseAsync<Receipt>([systemMessage, llamaMessage],
                                                                                   new ChatOptions { Temperature = 0 });

               // var response = await chatClient.GetStreamingResponseAsync([systemMessage, message],
               //                                                           new ChatOptions { Temperature = 0 }).StreamToEndAsync().WaitAsync(TimeSpan.FromMinutes(30));
               File.AppendAllText("llama_response.txt",
                                  JsonSerializer.Serialize(llamaResponse) + "\n");
               return JsonSerializer.Serialize(llamaResponse);
           })
   .WithName("AI Calling");

app.MapPost("/aicalling",
            async (Messages messages) =>
            {
                var ollamaChatClient = app.Services.GetKeyedService<IChatClient>(messages.ModelName);
                List<ChatMessage> chatMessages = new ();

                foreach (var prompt in messages.Prompts)
                {
                    ChatMessage chatMessage = new ChatMessage(prompt.Role,
                                                              prompt.DefaultPrompt);

                    foreach (string promptContent in prompt.Contents)
                    {
                        chatMessage.Contents.Add(new TextContent(promptContent));
                    }

                    foreach (Image image in prompt.Images)
                    {
                        chatMessage.Contents.Add(new DataContent(image.ImageData,
                                                                 image.MediaType));
                    }

                    chatMessages.Add(chatMessage);
                }

                var ollamaResponse = ollamaChatClient.GetResponseAsync<Receipt>(chatMessages,
                                                                                 new ChatOptions { Temperature = 0 });
                
                return JsonSerializer.Serialize(ollamaResponse);
            })
   .WithName("AI Calling - POST");

app.Run();