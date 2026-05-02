using System.Net.Mime;
using System.Text;
using AI_ImageRacognition;
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
               var llamaChatClient    = app.Services.GetKeyedService<IChatClient>("llama");

               // var message = new ChatMessage(ChatRole.User,
               //                               """Extract all line items from this receipt. Respond in JSON format with this structure:{'CampanyName':'Company Name','items': [{ 'name': 'English item name(Chinese item name)', 'quantity': 1.500, 'unitPrice': 0.00, 'totalPrice': 0.00, 'Category': 'category', 'OnSale':true, 'Taxable':true }],  'subtotal': 0.00 }""");
               var deepseek_message = new ChatMessage(ChatRole.User,
                                                      File.ReadAllText("deepseek_prompt.txt",
                                                                       Encoding.UTF8));
               var llama_message = new ChatMessage(ChatRole.User,
                                                   File.ReadAllText("llama_prompt.txt",
                                                                    Encoding.UTF8));
               var systemMessage = new ChatMessage(ChatRole.System,
                                                   File.ReadAllText("system_prompt.txt",
                                                                    Encoding.UTF8));
               byte[] receiptBytes = File.ReadAllBytes("receipt.png");

               deepseek_message.Contents.Add(new DataContent(receiptBytes,
                                                             "image/png"));

               //var response = await chatClient.GetResponseAsync<Receipt>([systemMessage, message], new ChatOptions{ Temperature = 0});
               var deepseekResponse = await deepseekChatClient.GetResponseAsync([deepseek_message],
                                                                                new ChatOptions { Temperature = 0 });
               llama_message.Contents.Add(new TextContent(deepseekResponse.Text));
               llama_message.Contents.Add(new DataContent(receiptBytes,
                                                          "image/png"));
               var llamaResponse = await llamaChatClient.GetResponseAsync<Receipt>([systemMessage, llama_message],
                                                                                   new ChatOptions { Temperature = 0 });

               // var response = await chatClient.GetStreamingResponseAsync([systemMessage, message],
               //                                                           new ChatOptions { Temperature = 0 }).StreamToEndAsync().WaitAsync(TimeSpan.FromMinutes(30));
               return System.Text.Json.JsonSerializer.Serialize(llamaResponse);
           })
   .WithName("AI Calling");

app.Run();

record WeatherForecast(DateOnly Date,
                       int      TemperatureC,
                       string?  Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);
}