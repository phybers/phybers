#version 150 core

in vec3 vertexPos;			// Posicion de las fibras
in vec3 vertexNor;			// Normales 
in float vertexCol;			// Colores
in float vertex2Fib;

out vec3 vsNormal;
out float vsColor;
out float vsVertex2Fib;

void main() {
	
	vsNormal = vertexNor;
	vsColor = vertexCol;
	vsVertex2Fib = vertex2Fib;

	gl_Position = vec4(vertexPos, 1.0);
}