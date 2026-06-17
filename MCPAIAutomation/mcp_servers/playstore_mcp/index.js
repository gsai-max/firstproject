import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import gplay from "google-play-scraper";

// Initialize the server
const server = new Server(
  {
    name: "playstore-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Register tool listing handler
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_play_store_reviews",
        description: "Scrape public user reviews for a specific app from the Google Play Store.",
        inputSchema: {
          type: "object",
          properties: {
            appId: {
              type: "string",
              description: "The package name of the app (e.g. com.nextbillion.groww)",
            },
            lang: {
              type: "string",
              description: "Language code for the reviews (default: 'en')",
              default: "en",
            },
            country: {
              type: "string",
              description: "Country code for the reviews (default: 'in')",
              default: "in",
            },
            sort: {
              type: "string",
              description: "Sort order: 'newest', 'helpfulness', or 'rating' (default: 'newest')",
              enum: ["newest", "helpfulness", "rating"],
              default: "newest",
            },
            num: {
              type: "number",
              description: "Number of reviews to fetch per page (default: 100, max: 150)",
              default: 100,
            },
            nextPaginationToken: {
              type: "string",
              description: "Token for the next page of reviews (optional)",
            },
          },
          required: ["appId"],
        },
      },
    ],
  };
});

// Map sort values to google-play-scraper sort constants
const SORT_MAPPING = {
  newest: gplay.sort.NEWEST,
  helpfulness: gplay.sort.HELPFULNESS,
  rating: gplay.sort.RATING,
};

// Register tool execution handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name !== "get_play_store_reviews") {
    throw new Error(`Tool not found: ${name}`);
  }

  const appId = args?.appId;
  if (!appId) {
    return {
      isError: true,
      content: [
        {
          type: "text",
          text: "Missing required argument 'appId'",
        },
      ],
    };
  }

  const lang = args?.lang || "en";
  const country = args?.country || "in";
  const sort = args?.sort || "newest";
  const num = args?.num || 100;
  const nextPaginationToken = args?.nextPaginationToken;

  const playSort = SORT_MAPPING[sort] || gplay.sort.NEWEST;

  try {
    const options = {
      appId,
      lang,
      country,
      sort: playSort,
      num: Math.min(num, 150),
      paginate: true,
    };

    if (nextPaginationToken) {
      options.nextPaginationToken = nextPaginationToken;
    }

    const result = await gplay.reviews(options);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            reviews: result.data || [],
            nextPaginationToken: result.nextPaginationToken || null,
          }, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      isError: true,
      content: [
        {
          type: "text",
          text: `Failed to fetch reviews: ${error.message}`,
        },
      ],
    };
  }
});

// Start the server using stdio transport
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Play Store MCP server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error starting server:", error);
  process.exit(1);
});
