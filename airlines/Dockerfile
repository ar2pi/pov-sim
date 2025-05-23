# Step 1: Use an official Gradle image to build the application
FROM gradle:8.3.0-jdk17 AS build

# Set the working directory inside the container
WORKDIR /app

# Install curl
RUN apt-get update && apt-get install -y curl

# Copy the entire project to the container
COPY . .

# Build the application
RUN gradle clean bootJar

# Download the Grafana OpenTelemetry Java agent
RUN curl -sSLO https://github.com/grafana/grafana-opentelemetry-java/releases/download/v2.16.0/grafana-opentelemetry-java.jar

# Step 2: Use a lightweight JDK image for running the app
FROM openjdk:17-jdk-slim

# Set the working directory for the runtime container
WORKDIR /app

# Copy the JAR file from the build stage
COPY --from=build /app/build/libs/*.jar app.jar
# Copy the Grafana OpenTelemetry Java agent JAR file from the build stage
COPY --from=build /app/grafana-opentelemetry-java.jar .

# Expose the port the application runs on
EXPOSE 8080

# Set the command to run the application
ENTRYPOINT ["java", "-javaagent:grafana-opentelemetry-java.jar", "-jar", "app.jar"]
