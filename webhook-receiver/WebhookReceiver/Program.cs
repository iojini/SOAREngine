using WebhookReceiver.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new() { Title = "Webhook Receiver", Version = "v1" });
});

// Register HttpClient and SoarEngineService
builder.Services.AddHttpClient<SoarEngineService>();

var app = builder.Build();

// Configure pipeline
app.UseSwagger();
app.UseSwaggerUI();

app.MapControllers();

app.Run();