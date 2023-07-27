vec4 identityQ() {
	return vec4(0.0, 0.0, 0.0, 1.0);
}


vec4 multiplyQQ(vec4 leftQuaternion, vec4 rightQuaternion) {
	float lQw = leftQuaternion.w, lQx = leftQuaternion.x, lQy = leftQuaternion.y, lQz = leftQuaternion.z;
	float rQw = rightQuaternion.w, rQx = rightQuaternion.x, rQy = rightQuaternion.y, rQz = rightQuaternion.z;

	return vec4(lQw*rQw - lQx*rQx - lQy*rQy - lQz*rQz,
				lQx*rQw + lQw*rQx - lQz*rQy + lQy*rQz,
				lQy*rQw + lQz*rQx + lQw*rQy - lQx*rQz,
				lQz*rQw - lQy*rQx + lQx*rQy + lQw*rQz);
}


vec4 quaternionFromAngleAndAxis(float angle, vec3 axis) {
	float module = length(axis);
	float s = sin(angle/2.0) / module;

	return vec4(axis.x*s, axis.y*s, axis.z*s, cos(angle/2.0));
}


vec4 quaternionFromAngleAndAxis(float angle, float x, float y, float z) {
	float module = sqrt(x*x + y*y + z*z);
	float s = sin(angle/2.0) / module;

	return vec4(x*s, y*s, z*s, cos(angle/2.0));
}


vec4 quaternionFromElements(float x, float y, float z, float w) {
	return vec4(w, x, y, z);
}


vec4 quaternionFromQuaternion(vec4 fromQuaternion) {
	return vec4(fromQuaternion);
}


vec4 normalizeQ(vec4 quaternion) {
	// float module = length(quaternion);

	// return vec4(quaternion / module);
	return normalize(quaternion);
}


vec4 invertQ(vec4 fromQuaternion) {
	return vec4(-fromQuaternion.xyz, fromQuaternion.w);
}


vec3 rotateVec3Q(vec3 vector, vec4 quaternion) {
	vec4 p = quaternionFromElements(vector.x, vector.y, vector.z, 0.0);
	vec4 invertedQuaternion = invertQ(quaternion);
	vec4 res = multiplyQQ(p, invertedQuaternion);
	res = multiplyQQ(quaternion, res);

	return res.xyz;
}


vec4 rotateVec4Q(vec4 vector, vec4 quaternion) {
	vec4 p = quaternionFromElements(vector.x, vector.y, vector.z, 0.0);
	vec4 invertedQuaternion = invertQ(quaternion);
	vec4 res = multiplyQQ(p, invertedQuaternion);
	res = multiplyQQ(quaternion, res);

	return vec4(res.xyz, vector.w);
}


mat3 rotationMat3Q(vec4 quaternion){
	float xx = quaternion.x*quaternion.x;
	float yy = quaternion.y*quaternion.y;
	float zz = quaternion.z*quaternion.z;
	float xy = quaternion.x*quaternion.y;
	float wz = quaternion.w*quaternion.z;
	float xz = quaternion.x*quaternion.z;
	float wy = quaternion.w*quaternion.y;
	float yz = quaternion.y*quaternion.z;
	float wx = quaternion.w*quaternion.x;

	return mat3(1.0-2.0*(yy+zz),	2.0*(xy+wz),	2.0*(xz-wy),
				2.0*(xy-wz),		1.0-2.0*(xx+zz),2.0*(yz+wx),
				2.0*(xz+wy),		2.0*(yz-wx),	1.0-2.0*(xx+yy));
}


mat4 rotationMat4Q(vec4 quaternion){
	float xx = quaternion.x*quaternion.x;
	float yy = quaternion.y*quaternion.y;
	float zz = quaternion.z*quaternion.z;
	float xy = quaternion.x*quaternion.y;
	float wz = quaternion.w*quaternion.z;
	float xz = quaternion.x*quaternion.z;
	float wy = quaternion.w*quaternion.y;
	float yz = quaternion.y*quaternion.z;
	float wx = quaternion.w*quaternion.x;

	return mat4(1.0-2.0*(yy+zz),	2.0*(xy+wz),	2.0*(xz-wy),	0.0,
				2.0*(xy-wz),		1.0-2.0*(xx+zz),2.0*(yz+wx),	0.0,
				2.0*(xz+wy),		2.0*(yz-wx),	1.0-2.0*(xx+yy),0.0,
				0.0,				0.0,			0.0,			1.0);
}


vec3 getAxisFromQuaternion(vec4 quaternion) {
	float sin2 = sqrt(1.0-quaternion.w*quaternion.w);

	return quaternion.xyz/sin2;
}


float getAngleFromQuaternion(vec4 quaternion) {
	return acos(quaternion.w)*2.0;
}


// void slerp(float[] resQ, int rqOffset, float[] originQ, int oqOffset, float[] destinationQ, int dqOffset, float step){
// 	float[] tmpQ = new float[4];
// 	float[] invertedOriginQ = new float[4];
// 	invert(invertedOriginQ, 0, originQ, oqOffset);

// 	multiplyQQ(tmpQ,0, destinationQ, dqOffset, invertedOriginQ,0);
// 	scaleQuaternionIn(tmpQ,0, tmpQ,0, step);

// 	multiplyQQ(resQ, rqOffset, tmpQ,0, originQ, oqOffset);
// }


// static public void scaleQuaternionIn(float[] resQ, int rqOffset, float[] quaternion, int qOffset, float step) {
// 	float[] axis = new float[3];
// 	float angle = toAngleAxis(axis,0, quaternion, qOffset);

// 	fromAngleAndAxis(resQ, rqOffset, angle*step, axis[0], axis[1], axis[2]);
// }
