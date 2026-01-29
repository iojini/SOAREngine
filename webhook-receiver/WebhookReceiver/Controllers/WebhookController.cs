using Microsoft.AspNetCore.Mvc;
using WebhookReceiver.Models;
using WebhookReceiver.Services;

namespace WebhookReceiver.Controllers;

[ApiController]
[Route("api/[controller]")]
public class WebhookController : ControllerBase
{
    private readonly SoarEngineService _soarEngineService;
    private readonly ILogger<WebhookController> _logger;

    public WebhookController(
        SoarEngineService soarEngineService,
        ILogger<WebhookController> logger)
    {
        _soarEngineService = soarEngineService;
        _logger = logger;
    }

    /// <summary>
    /// Receive a webhook alert and forward to SOAREngine
    /// </summary>
    [HttpPost("alert")]
    public async Task<ActionResult<WebhookResponse>> ReceiveAlert([FromBody] AlertPayload payload)
    {
        _logger.LogInformation("Received webhook alert: {Title}", payload.Title);

        var result = await _soarEngineService.ForwardAlertAsync(payload);

        if (result != null)
        {
            return Ok(new WebhookResponse
            {
                Success = true,
                Message = "Alert forwarded to SOAREngine successfully",
                AlertId = result.Id
            });
        }

        return StatusCode(502, new WebhookResponse
        {
            Success = false,
            Message = "Failed to forward alert to SOAREngine"
        });
    }

    /// <summary>
    /// Receive generic webhook payload
    /// </summary>
    [HttpPost("generic")]
    public async Task<ActionResult<WebhookResponse>> ReceiveGeneric([FromBody] Dictionary<string, object> payload)
    {
        _logger.LogInformation("Received generic webhook with {Count} fields", payload.Count);

        // Convert generic payload to alert
        var alert = new AlertPayload
        {
            Title = payload.GetValueOrDefault("title")?.ToString() ?? "Generic Webhook Alert",
            Description = payload.GetValueOrDefault("description")?.ToString(),
            Severity = payload.GetValueOrDefault("severity")?.ToString() ?? "medium",
            Source = payload.GetValueOrDefault("source")?.ToString() ?? "webhook",
            SourceIp = payload.GetValueOrDefault("source_ip")?.ToString(),
            RawData = payload
        };

        var result = await _soarEngineService.ForwardAlertAsync(alert);

        if (result != null)
        {
            return Ok(new WebhookResponse
            {
                Success = true,
                Message = "Generic webhook processed and forwarded",
                AlertId = result.Id
            });
        }

        return StatusCode(502, new WebhookResponse
        {
            Success = false,
            Message = "Failed to process webhook"
        });
    }

    /// <summary>
    /// Health check endpoint
    /// </summary>
    [HttpGet("health")]
    public ActionResult<object> Health()
    {
        return Ok(new
        {
            Status = "healthy",
            Service = "WebhookReceiver",
            Timestamp = DateTime.UtcNow
        });
    }
}