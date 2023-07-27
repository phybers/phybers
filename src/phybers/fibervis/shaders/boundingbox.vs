#version 150 core

// Datos de entrada
in vec3 vertexPos;

// Datos de salida
out vec4 color;

uniform mat4 M;
uniform mat4 bbM;
uniform mat4 V;
uniform mat4 P;


void main() {
    color = vec4(1.0, 1.0, 1.0, 1.0);
    gl_Position = P*V*M*bbM*vec4(vertexPos, 1.0);
}
