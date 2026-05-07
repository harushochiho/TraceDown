FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
USER $APP_UID
WORKDIR /app
ENV ASPNETCORE_URLS="http://+:8801;http://+:8802"
EXPOSE 8801
EXPOSE 8802

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["AI_ImageRacognition/AI_ImageRacognition.csproj", "AI_ImageRacognition/"]
RUN dotnet restore "AI_ImageRacognition/AI_ImageRacognition.csproj"
COPY . .
WORKDIR "/src/AI_ImageRacognition"
RUN dotnet build "./AI_ImageRacognition.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./AI_ImageRacognition.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "AI_ImageRacognition.dll"]
