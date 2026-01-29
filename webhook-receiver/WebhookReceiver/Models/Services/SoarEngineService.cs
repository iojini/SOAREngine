using System.Text;
using System.Text.Json;
using WebhookReceiver.Models;

namespace WebhookReceiver.Services;

public class SoarEngineService
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _configuration;
    private readonly ILogger<SoarEngineService> _logger;

    public SoarEngineService(
        HttpClient httpClient,
        IConfiguration configuration,
        ILogger<SoarEngineService> logger)
    {
        _httpClient = httpClient;
        _configuration = configuration;
        _logger = logger;
    }

    public async Task<SoarEngineResponse?> ForwardAlertAsync(AlertPayload alert)
    {
        var soarEngineUrl = _configuration["SoarEngine:BaseUrl"] ?? "http://localhost:8000";
        var apiKey = _configuration["SoarEngine:ApiKey"] ?? "";

        var payload = new
        {
            title = alert.Title,
            description = alert.Description,
            severity = alert.Severity.ToLower(),
            source = alert.Source.ToLower(),
            source_ip = alert.SourceIp,
            destination_ip = alert.DestinationIp,
            domain = alert.Domain,
            file_hash = alert.FileHash
        };

        var json = JsonSerializer.Serialize(payload);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        _httpClient.DefaultRequestHeaders.Clear();
        if (!string.IsNullOrEmpty(apiKey))
        {
            _httpClient.DefaultRequestHeaders.Add("X-API-Key", apiKey);
        }

        try
        {
            _logger.LogInformation("Forwarding alert to SOAREngine: {Title}", alert.Title);
            
            var response = await _httpClient.PostAsync($"{soarEngineUrl}/alerts/", content);
            
            if (response.IsSuccessStatusCode)
            {
                var responseBody = await response.Content.ReadAsStringAsync();
                var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                var result = JsonSerializer.Deserialize<SoarEngineResponse>(responseBody, options);
                
                _logger.LogInformation("Alert forwarded successfully. ID: {AlertId}", result?.Id);
                return result;
            }
            else
            {
                _logger.LogError("Failed to forward alert. Status: {StatusCode}", response.StatusCode);
                return null;
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error forwarding alert to SOAREngine");
            return null;
        }
    }
}