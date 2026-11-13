import fs from "node:fs";
import yaml from "js-yaml";
import markdownIt from "markdown-it";
import { HtmlBasePlugin } from "@11ty/eleventy";

const read = (f) => fs.readFileSync(new URL(f, import.meta.url), "utf8");

export default function (cfg) {
  cfg.addDataExtension("yaml", (c) => yaml.load(c));
  cfg.addPlugin(HtmlBasePlugin); // rewrites absolute links with pathPrefix
  cfg.addPassthroughCopy({ "src/assets": "assets" });
  cfg.addGlobalData("helpers", {
    duckdb: read("./helpers/duckdb.sql"),
    postgres: read("./helpers/postgres.sql"),
    mongo: read("./helpers/mongo.js"),
    jq: read("./helpers/pattern.jq"),
  });

  // "Date/Time as String" -> "date-time-as-string"
  cfg.addFilter("smellSlug", (s) => s.toLowerCase().replaceAll("/", "-").replaceAll(" ", "-"));
  const md = markdownIt({ html: true });
  cfg.setLibrary("md", md);
  cfg.addFilter("mdInline", (s) => md.renderInline(s ?? ""));
  // Reference keys -> ABNT entries, alphabetical as NBR 6023 requires. No keys = all.
  cfg.addFilter("abnt", function (keys) {
    const refs = this.ctx.referencias;
    return [...new Set(keys ?? Object.keys(refs))].map((k) => refs[k].abnt).sort((a, b) => a.localeCompare(b, "pt-BR"));
  });

  return {
    dir: { input: "src", output: "_site" },
    pathPrefix: "/data-smell-wiki/",
    markdownTemplateEngine: "njk",
  };
}
