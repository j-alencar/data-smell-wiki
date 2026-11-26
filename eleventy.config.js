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

  // Wikipedia-style citations: [@key] or [@key, p. 12] in any page becomes a numbered
  // superscript, and <!--referencias--> becomes the list of the references cited there.
  const refs = yaml.load(read("./src/_data/referencias.yaml"));
  cfg.addTransform("citacoes", function (html) {
    if (!this.page.outputPath?.endsWith(".html")) return html;
    const nums = new Map(); // key -> {n, uses}
    // Leave code blocks alone: jq and SQL may contain "[@".
    const parts = html.split(/(<pre[\s\S]*?<\/pre>)/);
    for (let i = 0; i < parts.length; i += 2) {
      parts[i] = parts[i].replace(/\[@([\w-]+)(?:, ([^\]]+))?\]/g, (_, key, loc) => {
        if (!refs[key]) throw new Error(`${this.page.inputPath}: unknown citation [@${key}]`);
        if (!nums.has(key)) nums.set(key, { n: nums.size + 1, uses: 0 });
        const c = nums.get(key);
        c.uses += 1;
        const where = loc ? `<span class="loc">:${loc.replace(/^p\. /, "")}</span>` : "";
        return `<sup class="cite" id="cite-${c.n}-${c.uses}"><a href="#ref-${c.n}">[${c.n}]</a>${where}</sup>`;
      });
    }
    const lista = [...nums].map(([key, { n, uses }]) => {
      const back =
        uses === 1
          ? `<a href="#cite-${n}-1" class="back">^</a>`
          : `^ ${Array.from({ length: uses }, (_, u) => `<a href="#cite-${n}-${u + 1}" class="back">${String.fromCharCode(97 + u)}</a>`).join(" ")}`;
      return `<li id="ref-${n}">${back} ${md.renderInline(refs[key].abnt)}</li>`;
    });
    const secao = lista.length ? `<h2 id="referencias">Referências</h2>\n<ol class="refs">\n${lista.join("\n")}\n</ol>` : "";
    return parts.join("").replace("<!--referencias-->", secao);
  });

  return {
    dir: { input: "src", output: "_site" },
    pathPrefix: "/data-smell-wiki/",
    markdownTemplateEngine: "njk",
  };
}
