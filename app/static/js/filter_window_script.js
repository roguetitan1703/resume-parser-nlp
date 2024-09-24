let NERArrays = {
  // external_links: {
  //   github: ["github.com"],
  //   linkedin: ["linkedin.com"],
  //   hackerrank: ["hackerrank.com"],
  //   leetcode: ["leetcode.com"],
  //   codechef: ["codechef.com"],
  //   codingninjas: ["codingninjas.com"],
  // },
  // social_links: {
  //   instagram: ["instagram.com"],
  //   twitter: ["twitter.com", "x.com"],
  //   facebook: ["facebook.com"],
  // },
  external_links: [
    "github.com",
    "linkedin.com",
    "hackerrank.com",
    "leetcode.com",
    "codechef.com",
    "codingninjas.com",
  ],
  social_links: ["instagram.com", "twitter.com", "facebook.com"],
  programming_languages: [
    "python",
    "java",
    "javascript",
    "js",
    "c#",
    "c-sharp",
    "c++",
    "cpp",
    "ruby",
    "go",
    "golang",
    "swift",
    "kotlin",
    "php",
    "typescript",
    "ts",
    "scala",
    "rust",
    "perl",
    "clojure",
    "bash",
    "shell",
    "objective-c",
    "dart",
    "r",
    "matlab",
    "elixir",
    "haskell",
    "lua",
    "erlang",
    "f#",
    "fortran",
    "cobol",
    "sas",
  ],
  frameworks: [
    "django",
    "flask",
    "react",
    "react.js",
    "angular",
    "angular.js",
    "vue.js",
    "vue",
    "spring",
    "spring boot",
    "asp.net",
    "ruby on rails",
    "express.js",
    "express",
    "node.js",
    "node",
    "laravel",
    "symfony",
    "ember.js",
    "backbone.js",
    "next.js",
    "nuxt.js",
    "svelte",
    "pyramid",
    "fastapi",
    "bottle",
    "phoenix",
    "meteor",
    "gatsby",
    "blazor",
    "uikit",
  ],
  databases: [
    "mysql",
    "postgresql",
    "postgres",
    "mongodb",
    "oracle",
    "sql server",
    "sqlserver",
    "ms sql",
    "ms-sql",
    "sqlite",
    "redis",
    "cassandra",
    "mariadb",
    "elasticsearch",
    "db2",
    "couchdb",
    "dynamodb",
    "neo4j",
    "influxdb",
    "hbase",
    "firebase",
    "firestore",
    "cockroachdb",
    "memcached",
    "sql",
  ],
  tools: [
    "git",
    "docker",
    "kubernetes",
    "jenkins",
    "aws",
    "azure",
    "gcp",
    "google cloud platform",
    "tensorflow",
    "pytorch",
    "postman",
    "visual studio code",
    "vs code",
    "intellij idea",
    "intellij",
    "eclipse",
    "jira",
    "slack",
    "bitbucket",
    "circleci",
    "travisci",
    "heroku",
    "rancher",
    "openshift",
    "gitlab",
    "kibana",
    "airflow",
    "hadoop",
    "jupyter",
    "databricks",
    "zepl",
  ],
  cloud_platforms: [
    "aws",
    "azure",
    "google cloud platform",
    "gcp",
    "ibm cloud",
    "oracle cloud",
    "alibaba cloud",
    "digitalocean",
    "linode",
    "rackspace",
    "cloudflare",
  ],
  devops_tools: [
    "jenkins",
    "ansible",
    "terraform",
    "terraform cloud",
    "puppet",
    "chef",
    "nagios",
    "prometheus",
    "prom",
    "grafana",
    "splunk",
    "docker swarm",
    "saltstack",
    "new relic",
    "elk stack",
    "zabbix",
  ],
  frontend_technologies: [
    "html",
    "css",
    "bootstrap",
    "tailwind css",
    "materialize",
    "bulma",
    "foundation",
    "semantic ui",
    "sass",
    "less",
    "stylus",
  ],
};

// Instead of having the NERArrays read the record.json as it changes in the filter words to display in the sidebar
async function loadNERArrays() {
  try {
    const response = await fetch("/static/record.json");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    NERArrays = await response.json();
    console.log(NERArrays, "NERArrays");

    return NERArrays;
  } catch (error) {
    console.error("Error fetching JSON:", error);
  }
}

// const NERArrays = json["NERArrays"];
const filterContainer = document.getElementById("filter-container");

function createFilterCheckbox(category, label) {
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.id = `filter-${category}-${label}`;
  checkbox.classList.add("mr-2");

  const labelElement = document.createElement("label");
  labelElement.classList.add("text-sm");
  labelElement.textContent = label;
  labelElement.htmlFor = checkbox.id;

  const container = document.createElement("div");
  const classList =
    "overflow-hidden p-1 px-2 mr-4 mb-2 text-slate-50 rounded-full rounded-md rounded-sm border-2 ring-1 ring-black shadow-md flex flex-row items-center hover:bg-white hover:text-gray-900 transition ease-in-out";
  container.classList.add(...classList.split(" "));
  container.appendChild(checkbox);
  container.appendChild(labelElement);

  return container;
}

function createFilterSection(category, data) {
  const section = document.createElement("div");
  section.classList.add("border-b", "pb-2", "mb-4");

  const title = document.createElement("h3");
  title.classList.add("font-bold", "mb-4", "text-xl");
  title.textContent = category;

  section.appendChild(title);

  const container = document.createElement("div");
  container.classList.add("grid", "items-center", "grid-cols-4");

  console.log(category, data);
  data.forEach((label) => {
    container.appendChild(createFilterCheckbox(category, label));
  });

  section.appendChild(container);

  return section;
}

function generateFilterSidebar() {
  console.log("going through the NER arrays", NERArrays);
  for (const category in NERArrays) {
    console.log(category, NERArrays[category]);
    const section = createFilterSection(category, NERArrays[category]);

    filterContainer.appendChild(section);
  }
}

// Wait for DOM content to load before generating the filter sidebar
document.addEventListener("DOMContentLoaded", function () {
  // make an async function to load the NERArrays and generate Filter side bar
  loadNERArrays();

  generateFilterSidebar();

  document
    .getElementById("download")
    .addEventListener("click", async function () {
      try {
        // Fetch data from MongoDB (replace with your actual fetch URL)
        const collectionName = "{{ collection_name }}"; // Assuming this is passed from the backend
        const response = await fetch(
          `/get_resume_data?collection=${collectionName}`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }

        // Convert fetched data to JSON
        const data = await response.json();

        // Convert the JSON object to a string
        const jsonData = JSON.stringify(data, null, 2); // Pretty-printed JSON

        // Create a Blob with the JSON data
        const blob = new Blob([jsonData], { type: "application/json" });

        // Create a temporary URL for the Blob
        const url = URL.createObjectURL(blob);

        // Create a temporary download link element
        const link = document.createElement("a");
        link.href = url;
        link.download = `${collectionName}_analysis.json`; // Naming the file

        // Programmatically click the link to trigger the download
        link.click();

        // Clean up the temporary URL
        URL.revokeObjectURL(url);
      } catch (error) {
        console.error("Error downloading data:", error);
      }
    });

  // setTimeout(() => generateFilterSidebar(), 1000);
});
