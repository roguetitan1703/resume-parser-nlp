NER_ARRAYS = {
    "external_links": {
        "github": ["github.com"],
        "linkedin": ["linkedin.com"],
        "hackerrank": ["hackerrank.com"],
        "leetcode": ["leetcode.com"],
        "codechef": ["codechef.com"],
        "codingninjas": ["codingninjas.com"]
    },
    "social_links": {
        "instagram": ["instagram.com"],
        "twitter": ["twitter.com", "x.com"],
        "facebook": ["facebook.com"]
    },
    "programming_languages": [
        "python", "java", "javascript", "js", "c#", "c-sharp", "c++", "cpp", "ruby",
        "go", "golang", "swift", "kotlin", "php", "typescript", "ts", "scala", "rust",
        "perl", "clojure", "bash", "shell", "objective-c", "dart", "r", "matlab",
        "elixir", "haskell", "lua", "erlang", "f#", "fortran", "cobol", "sas"
    ],
    "frameworks": [
        "django", "flask", "react", "react.js", "angular", "angular.js", "vue.js", "vue",
        "spring", "spring boot", "asp.net", "ruby on rails", "express.js", "express",
        "node.js", "node", "laravel", "symfony", "ember.js", "backbone.js", "next.js",
        "nuxt.js", "svelte", "pyramid", "fastapi", "bottle", "phoenix", "meteor",
        "gatsby", "blazor", "uikit",
    ],
    "databases": [
        "mysql", "postgresql", "postgres", "mongodb", "oracle", "sql server",
        "sqlserver", "ms sql", "ms-sql", "sqlite", "redis", "cassandra", "mariadb",
        "elasticsearch", "db2", "couchdb", "dynamodb", "neo4j", "influxdb", "hbase",
        "firebase", "firestore", "cockroachdb", "memcached", "sql"
    ],
    "tools": [
        "git", "docker", "kubernetes", "jenkins", "aws", "azure", "gcp",
        "google cloud platform", "tensorflow", "pytorch", "postman", "visual studio code",
        "vs code", "intellij idea", "intellij", "eclipse", "jira", "slack", "bitbucket",
        "circleci", "travisci", "heroku", "rancher", "openshift", "gitlab", "kibana",
        "airflow", "hadoop", "jupyter", "databricks", "zepl"
    ],
    "cloud_platforms": [
        "aws", "azure", "google cloud platform", "gcp", "ibm cloud", "oracle cloud",
        "alibaba cloud", "digitalocean", "linode", "rackspace", "cloudflare"
    ],
    "devops_tools": [
        "jenkins", "ansible", "terraform", "terraform cloud", "puppet", "chef", "nagios",
        "prometheus", "prom", "grafana", "splunk", "docker swarm", "saltstack",
        "new relic", "elk stack", "zabbix"
    ],
    "frontend_technologies": [
        "html", "css", "bootstrap", "tailwind css", "materialize", "bulma", "foundation",
        "semantic ui", "sass", "less", "stylus"
    ]
}

EMAIL_REGEX = r'[^.]([a-zA-Z0-9._%+-]+[^.])@([a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)(\s*\.[a-zA-Z]{2,})'

PHONE_REGEX = r"(?:\+?\d{1,3}[\s-]?)?(?:\(\d{3}\)|\d{3})[\s-]?\d{2,4}[\s-]?\d{2,4}"

EDUCATION_WORDS = ["educational","university", "college", "institute", "school", "academy", "faculty", "polytechnic","iit","nit","mit",'iiit',"bit","vit","viit","bachelor", "master", "phd", "degree", "graduate","pursuing","btech","b.tech","m.tech","mtech","mba","ba","bsc","ma","msc","mca","mcom","bcom","bca","bba"]