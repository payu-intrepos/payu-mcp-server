# PayU MCP Server

**Seamlessly integrate PayU payment services with your AI tools through Model Context Protocol**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10-green)](https://www.python.org/downloads/release/python-3100/)

## Overview

PayU MCP Server provides specialized integration that enables AI tools to securely access PayU payment APIs through the Model Context Protocol (MCP). This integration allows AI assistants to create payment links, retrieve transaction details, and access invoice information directly, making your payment workflows smarter and more efficient.

## What is the Model Context Protocol (MCP)?

> The Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. Whether you're building an AI-powered IDE, enhancing a chat interface, or creating custom AI workflows, MCP provides a standardized way to connect LLMs with the context they need.
>
> &mdash; [Model Context Protocol](https://github.com/modelcontextprotocol)

## Available Tools

| Tool Name | Description |
|-------------------------------|---------------------------------------------------------------|
| **create-payment-link** | Generate a new payment link for your customers |
| **get-invoice-details** | Retrieve comprehensive details for any invoice ID |
| **get-transaction-details** | Access complete transaction information |

## Getting Started

### Prerequisites

- Python 3.10 or higher
- PayU Merchant Account with API access
- MCP-compatible AI client (Claude AI, etc.)

### Installation

#### Option 1: Standard Installation

##### 1. Clone the Repository

```bash
git clone https://github.com/payu-intrepos/payu-mcp-server.git
cd payu-mcp-server
```

##### 2. Install Dependencies

We recommend using `uv` for Python dependency management. Install uv from [Astral](https://docs.astral.sh/uv/getting-started/installation/).

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and activate it
uv venv
source .venv/bin/activate

# Install dependencies
uv add "mcp[cli]" httpx python-dotenv
```

Alternatively, you can use pip:

```bash
pip install -r requirements.txt
```

#### Option 2: Docker Installation

##### 1. Clone the Repository

```bash
git clone https://github.com/payu-intrepos/payu-mcp-server.git
cd payu-mcp-server
```

##### 2. Build Docker Image

```bash
docker build -t payu-mcp-server .
```

##### 3. Run Docker Container

Run the container with your PayU credentials:


```bash
docker run -p 8888:8888 \
  -e CLIENT_ID="YOUR_CLIENT_ID" \
  -e CLIENT_SECRET="YOUR_CLIENT_SECRET" \
  -e MERCHANT_ID="YOUR_MERCHANT_ID" \
  -e PORT=8888 \
  payu-mcp-server python server.py --sse --port 8888
```

### 3. Add Server to MCP Client Configuration

**Example for Claude AI Desktop Client:**

Location of configuration file:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

#### For Standard Installation:

Add the following to your configuration:

```json
{
  "mcpServers": {
    "payu-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/payu-mcp-server",
        "run",
        "server.py"
      ],
      "env": {
        "CLIENT_ID": "YOUR_CLIENT_ID",
        "CLIENT_SECRET": "YOUR_CLIENT_SECRET",
        "MERCHANT_ID": "YOUR_MERCHANT_ID"
      }
    }
  }
}
```

#### For Docker Installation:

Configure your MCP client to connect to the Docker container:

```json
{
  "mcpServers": {
    "payu-mcp-server": {
      "url": "http://localhost:8888"
    }
  }
}
```

## API Credentials

To obtain your API credentials, visit the [PayU Developer Portal](https://docs.payu.in/docs/get-client-id-and-secret-from-dashboard).

Required credentials:
- **CLIENT_ID**: Your PayU client ID
- **CLIENT_SECRET**: Your PayU client secret
- **MERCHANT_ID**: Your PayU merchant identifier

### Additional Permission Scopes

When configuring your API access, ensure you have the following permission scopes:

- **read_transactions**: 
  - Provides access to transaction history and details
  - Allows retrieval of transaction metadata.
  - Enables detailed transaction analysis and tracking


- **read_invoices**:
  - Enables fetching comprehensive invoice details
  - Provides access to invoice status, amounts, and related transaction information
  - Read-only permission ensures secure access to invoice data

Note: Contact PayU support to confirm these specific scopes are available and properly configured for your merchant account.

## Usage Examples

### Creating a Payment Link 

Once configured, your MCP Client can create payment links with a natural language request:

1. Payment link with contacts 

```
Create a payment link for ₹5000 for Web Development Services and send to ABC
```
2. Payment link with email 

```
Create a payment link for ₹5000 for Web Development Services and send to <abc@example.com>

```



### Fetching transactions for Invoice Number/Payment Link

Once configured, your AI assistant can help you fetch invoice number details with a natural language request:

```
Get the invoice details for <Invoice-ID>
```

### Fetching details for any transaction

Once configured, your AI assistant can help you fetch transaction details with a natural language request:

```
Provide the transaction details for <Transaction-ID>
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.