---
status: accepted
---

# ECS Fargate over Lambda for the Flask origin

CloudFront needs a live origin to serve the Jinja2-rendered routes on cache misses (first view of a paste, the create form, `jinja2-fragments` htmx endpoints). Lambda behind a WSGI adapter (e.g. Zappa) was considered, since it fits the otherwise-serverless shape of the rest of the stack (DynamoDB, S3+CloudFront for static assets).

Lambda was rejected because Flask's execution model is a poor match for it: Flask runs as long-lived gunicorn worker processes, not discrete request handlers, and a WSGI-on-Lambda adapter reintroduces cold starts on scale-from-zero — directly undermining the fast-render requirement on exactly the requests that matter most (cache misses, which are the requests CloudFront can't shortcut). A warm, always-running process avoids that entirely.

Decision: Flask runs on ECS Fargate, behind an Application Load Balancer, which CloudFront uses as its origin for non-static routes.
