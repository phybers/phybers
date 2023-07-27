// Fragment shader del volume render.

// Aqui se ilumina el modelo del volume render, ademas de dibujar los ROIs presentes.
// mriTexture y roiTexture contienen texturas volumetricas con la informacion para
// la visualizacion de los datos.

// Para la iluminacion usa los algoritmos blinn-phong o cook-tottance.
// La normal la calcula como la estimacion del gradiente en el volumen, usando un
// pequenio DELTA.

// El tipo de visualizacion (suave o cubos) dependera de mode.

// ****** Aun no esta funcionando en el programa ********

#version 150

#define DELTA (0.005)

// uniforms for the textures
uniform sampler3D mriTexture;

// threshold for realtime thresholding
uniform float threshold;

// uniform for displaying the texture
uniform float slope;

uniform mat4 M;

uniform vec3 eye;

uniform mat3 axis;

in vec3 texCoord;
in vec3 positionOut;

out vec4 outColor;

uniform float alpha;


// Blinn-Phong illumination
vec3 blinn_phong_shading(vec3 N, vec3 L, vec3 V);


// Cook-Torrance illumination
vec3 cook_torrance_shading(vec3 N, vec3 L, vec3 V);


vec3 gradientEstimation(sampler3D textureIdx, vec3 textureCoor);


void main(void) {
    // TMP ////////////////////////
    if (texCoord.x < 0.01 || texCoord.x >0.99 || texCoord.y < 0.01 || texCoord.y >0.99 || texCoord.z < 0.01 || texCoord.z >0.99) discard;
	/////////////////////////////////
	
	float intensity = texture(mriTexture, texCoord).r;

	if (intensity < threshold)
		discard;

	// Central difference and normalization / calculate light - and viewing direction
	vec3 N = /*(vec4(*/axis * gradientEstimation(mriTexture, texCoord);//, 1.0)).xyz;
	vec3 L = normalize(eye - positionOut);	// light position
	vec3 V = normalize(eye - positionOut);

	// Local illumination
	float grey = intensity*slope;
	outColor = vec4(blinn_phong_shading(N,L,V) + grey, alpha);;
}


// DEBERIA SER PONDERADO POR EL TAMANIO DEL VOXEL
vec3 gradientEstimation(sampler3D textureIdx, vec3 textureCoor) {
	vec3 sample1, sample2;

	// six texture samples for the gradient
	// LAST MODIFY: CHANGE DIRECTION OF GRADIENT ON X AND Z AXIS.
	sample1.x = texture(textureIdx, textureCoor+vec3(DELTA,0.0,0.0)).r;
	sample2.x = texture(textureIdx, textureCoor-vec3(DELTA,0.0,0.0)).r;
	sample1.y = texture(textureIdx, textureCoor-vec3(0.0,DELTA,0.0)).r;
	sample2.y = texture(textureIdx, textureCoor+vec3(0.0,DELTA,0.0)).r;
	sample1.z = texture(textureIdx, textureCoor+vec3(0.0,0.0,DELTA)).r;
	sample2.z = texture(textureIdx, textureCoor-vec3(0.0,0.0,DELTA)).r;

	return normalize(sample2-sample1);
}


vec3 blinn_phong_shading(vec3 N, vec3 L, vec3 V) {
	// material properties
	float Ka = 0.1;		// ambient
	float Kd = 0.6;		// diffuse
	float Ks = 0.2;		// specular
	float n = 100.0;	// shininess

	// light properties
	vec3 lightColor = vec3(1.0, 1.0, 1.0);
	vec3 ambientLight = vec3(0.3, 0.3, 0.3);

	// Calculate halfway vector
	vec3 H = normalize(L + V);

	// Compute ambient term
	vec3 ambient = Ka * ambientLight;

	// Compute the diffuse term
	float diffuseLight = max(dot(L, N), 0);
	vec3 diffuse = Kd * lightColor * diffuseLight;

	// Compute the specular term
	float specularLight = pow(max(dot(H, N), 0), n); 
	if (diffuseLight <= 0) specularLight = 0;
	vec3 specular = Ks * lightColor * specularLight;

	return ambient + diffuse + specular;
}


vec3 cook_torrance_shading(vec3 N, vec3 L, vec3 V) {
	// material properties
	float Kd = 0.6; // diffuse
	float Ks = 0.2; // specular
	float mean  = 0.7; // mean value of microfacet distribution
	float scale = 0.2; // constant factor C

	// light properties
	vec3 lightColor = vec3(1.0, 1.0, 1.0);

	vec3 H = normalize(L + V); 
	float n_h = dot(N,H);
	float n_v = dot(N,V);
	float v_h = dot(V,H);
	float n_l = dot(N,L);

	vec3 diffuse = vec3(Kd * max(n_l,0));
	// approximate Fresnel term
	float fresnel = pow(1.0 + v_h, 4);
	// approximate microfacet distribution 
	float delta = acos(n_h); // .x ????
	float exponent = -pow((delta/mean), 2);
	float microfacets = scale * exp(exponent);
	// calculate self-shadowing term
	float term1 = 2 * n_h * n_v/v_h;
	float term2 = 2 * n_h * n_l/v_h;
	float selfshadow = min(1,min(term1, term2));
	// calculate Cook-Torrance model
	vec3 specular = vec3(Ks *fresnel *microfacets *selfshadow / n_v);

	return lightColor * (diffuse + specular);
}