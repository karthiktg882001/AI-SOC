# OpenAI Integration Setup

This AI SOC Assistant now uses OpenAI's GPT models to generate intelligent security analysis, summaries, and mitigation steps.

## Setup Instructions

### 1. Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy your API key (you won't be able to see it again!)

### 2. Configure the API Key

#### Option A: Docker Compose (Recommended)

Edit `docker-compose.yml` and add your OpenAI API key:

```yaml
ml-service:
  environment:
    OPENAI_API_KEY: "sk-your-api-key-here"
```

#### Option B: Environment Variable

Set the environment variable before running:

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
docker compose up -d
```

#### Option C: .env File

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-api-key-here
```

Then update `docker-compose.yml` to use it:

```yaml
ml-service:
  environment:
    OPENAI_API_KEY: ${OPENAI_API_KEY}
```

### 3. Restart Services

After adding the API key, restart the ML service:

```bash
docker compose restart ml-service
```

Or rebuild and restart:

```bash
docker compose build ml-service
docker compose up -d ml-service
```

## Features Using OpenAI

When OpenAI API key is configured, the following features use GPT models:

1. **Incident Summaries** - AI-generated executive summaries of security incidents
2. **Detailed Analysis** - Comprehensive technical analysis with IOCs and attack vectors
3. **Mitigation Steps** - Prioritized, actionable response steps
4. **Threat Analysis** - Context-aware threat assessment

## Fallback Behavior

If OpenAI API key is not set or API calls fail, the system automatically falls back to:
- Rule-based responses
- Template-based summaries
- Pattern-matched mitigation steps

This ensures the system continues to function even without OpenAI.

## Model Used

- **Default Model**: `gpt-3.5-turbo` (cost-effective, fast)
- **Max Tokens**: 1000-1500 depending on the analysis type
- **Temperature**: 0.7 (balanced creativity and accuracy)

## Cost Considerations

OpenAI API usage is pay-per-use. Typical costs:
- **gpt-3.5-turbo**: ~$0.001-0.002 per incident analysis
- **gpt-4**: ~$0.03-0.06 per incident analysis (if configured)

Monitor your usage at [OpenAI Usage Dashboard](https://platform.openai.com/usage)

## Troubleshooting

### API Key Not Working

1. Verify the key is correct (starts with `sk-`)
2. Check your OpenAI account has credits
3. Review ML service logs: `docker logs aisoc-ml-service-1`
4. Look for "OpenAI client initialized successfully" message

### API Rate Limits

If you hit rate limits:
- The system will automatically fall back to rule-based responses
- Consider upgrading your OpenAI plan
- Or implement request throttling

### No AI Analysis Generated

1. Check logs for OpenAI errors
2. Verify API key is set correctly
3. Ensure internet connectivity from Docker container
4. Check OpenAI service status

## Security Best Practices

1. **Never commit API keys to Git**
2. Use environment variables or secrets management
3. Rotate API keys regularly
4. Monitor API usage for anomalies
5. Set usage limits in OpenAI dashboard

## Verification

After setup, test the integration:

1. Create a test incident
2. Generate an AI report
3. Check that the summary/analysis is more detailed than rule-based responses
4. Review logs to confirm OpenAI calls are successful

## Support

For issues:
- Check ML service logs: `docker logs aisoc-ml-service-1`
- Review OpenAI API status: https://status.openai.com/
- Verify API key permissions in OpenAI dashboard

