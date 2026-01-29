namespace WebhookReceiver.Models;

public class AlertPayload
{
    public string Title { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string Severity { get; set; } = "medium";
    public string Source { get; set; } = "webhook";
    public string? SourceIp { get; set; }
    public string? DestinationIp { get; set; }
    public string? Domain { get; set; }
    public string? FileHash { get; set; }
    public Dictionary<string, object>? RawData { get; set; }
}

public class WebhookResponse
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public string? AlertId { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

public class SoarEngineResponse
{
    public string Id { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
}