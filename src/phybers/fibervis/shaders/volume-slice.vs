// Vertex shader del volume render

// Dibuja con una llamada a instance draw.
// Dependiendo de la ubicacion de la camara, genera un numero X de slices perpendiculares a ella.
// Estos planos pueden ser de 3-6 vertices. Y son calculados en este shader. En colision con el bounding box.

// Los parametros del plano son cargados como unifom, al igual que los vectores v1, v2, etc.

// Este algoritmo es explicado en el libro "real-time volume render".


#version 150

// Render uniforms
uniform mat4 M;
uniform mat4 V;
uniform mat4 P;
uniform mat4 S;

// in attributes
in int vertexIdx;

// out attributes
out vec3 texCoord;
out vec3 positionOut;

// Volume-Slice static uniforms
uniform int v1[24];
uniform int v2[24];
uniform int nSequence[64];
uniform vec3 vertexPoints[8];

// Volume-Slice dinamic uniforms
uniform int frontIdx;
uniform vec4 np;
uniform float dPlane;
uniform float dPlaneStep;

void main (void) {
	for (int i=0; i<4; i++) {
		int vidx1 = nSequence[frontIdx*8 + v1[vertexIdx*4+i]];
		int vidx2 = nSequence[frontIdx*8 + v2[vertexIdx*4+i]];

		vec4 vertex1 = M * S * vec4(vertexPoints[vidx1], 1.0);
		vec4 vertex2 = M * S * vec4(vertexPoints[vidx2], 1.0);

		vec4 vertexStart = vertex1;
		vec4 e = vertex2 - vertex1;

		float denominator = dot(np, e);
		float lambda = denominator != 0.0 ? ((dPlane+dPlaneStep*gl_InstanceID)-dot(np, vertex1))/denominator : -1.0;

		if (lambda >= 0.0 && lambda <= 1.0) {
			positionOut = (vertexStart + lambda*e).xyz;
			
			texCoord = vertexPoints[vidx1] + lambda * (vertexPoints[vidx2]-vertexPoints[vidx1]);
			
			gl_Position = P * V * (vertexStart + lambda*e);
			return;
		}
	}
}