FROM debian:bookworm-slim

ARG HADOOP_VERSION=3.3.6
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    HADOOP_HOME=/opt/hadoop \
    HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop \
    HADOOP_VERSION=${HADOOP_VERSION}
ENV PATH="${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin:${JAVA_HOME}/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jdk-headless python3 openssh-server openssh-client \
    curl ca-certificates tar bash procps && \
    rm -rf /var/lib/apt/lists/*

# Instalación de Hadoop 3.3.6
RUN curl --fail --location --retry 3 \
    "https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz" \
    -o /tmp/hadoop.tar.gz && \
    tar -xzf /tmp/hadoop.tar.gz -C /opt && \
    mv "/opt/hadoop-${HADOOP_VERSION}" "$HADOOP_HOME" && \
    rm /tmp/hadoop.tar.gz

RUN useradd --create-home --shell /bin/bash alumno && \
    mkdir -p /run/sshd /data/output /data/input && \
    printf '%s\n' \
      'PasswordAuthentication no' \
      'PubkeyAuthentication yes' \
      'PermitRootLogin no' \
      'AllowUsers alumno' \
      > /etc/ssh/sshd_config.d/99-datamart.conf

# Configuración del sistema de archivos local
RUN printf '%s\n' \
    '<?xml version="1.0"?>' \
    '<configuration><property><name>fs.defaultFS</name><value>file:///</value></property></configuration>' \
    > "$HADOOP_CONF_DIR/core-site.xml" && \
    printf '%s\n' \
    '<?xml version="1.0"?>' \
    '<configuration><property><name>mapreduce.framework.name</name><value>local</value></property></configuration>' \
    > "$HADOOP_CONF_DIR/mapred-site.xml" && \
    printf 'export JAVA_HOME=%s\n' "$JAVA_HOME" >> "$HADOOP_CONF_DIR/hadoop-env.sh"

COPY hadoop/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
EXPOSE 22
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
