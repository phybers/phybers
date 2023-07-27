// ROIs segmentation.

// Octree datatype, build and defragmentation
#define OT_NODE_CAPACITY 256

struct OctreePool {
	struct OctreeNode *pool;
	unsigned **ce_pool;

	size_t pool_size;
	unsigned pool_idx;
};

struct OctreeNode {
	unsigned children[8]; 
	unsigned numberOfElements;
	unsigned contentElements;
	float radius[3];
	float center[3];
};


unsigned ROIsSegmentationPopulateAndDefragmentPool(void * pyOCPool,
	int octreePoolSize,
	void * pyPoints,
	int pointsSize,
	void * pyCenter,
	void * pyRadius,
	void * pyVertexIdxPool);


unsigned takeNodeFromPool(float *center, float * radius, struct OctreePool* nodePool);
bool octreeInsertVertex(struct OctreeNode* node, unsigned idx, float *vertexPool, struct OctreePool* nodePool);
void octreeSubdivide(struct OctreeNode* node, float *vertexPool, struct OctreePool* nodePool);
unsigned octreeRecursiveDefragment(struct OctreeNode* inNode, struct OctreePool* nodePool, unsigned *poolOffset, unsigned vertexIdxOffset, unsigned *vertexIdxPool, struct OctreeNode* swapNode, unsigned * childrenRefTMP);
void octreeDefragment();

// Octree collision query functions

struct ROI {
	float center[3];
	float radius[3];
	int roiType;
};

bool boundaryIntersectsSphere(struct ROI * sphere, struct OctreeNode * node);
bool sphereContainsVertex(struct ROI * sphere, float vertex_x, float vertex_y, float vertex_z);
bool SphereContainsBoundary(struct ROI * sphere, struct OctreeNode * node);
void querySphere(struct ROI * sphere, int nodeIdx, struct OctreeNode * nodePool, unsigned * vertex2Fiber, unsigned * vertexIdxPool, float * points, bool * result);

void queryTree(int nROI,
	void * roiDataArray,
	void * pyOCPool,
	void * pyVertexIdxPool,
	void * pyVertex2Fiber,
	void * pyPoints,
	void * pyResult,
	int curvesCount);

// Implementations

unsigned takeNodeFromPool(float *center, float * radius, struct OctreePool* nodePool) {
	if (nodePool->pool_idx >= nodePool->pool_size)
		return -1;

	unsigned idx = nodePool->pool_idx;
	struct OctreeNode *node = nodePool->pool+idx;

	node->center[0] = center[0];
	node->center[1] = center[1];
	node->center[2] = center[2];

	node->radius[0] = radius[0];
	node->radius[1] = radius[1];
	node->radius[2] = radius[2];

	memset(node->children, 0, 8*sizeof(unsigned));
	int i;
	for (i=0;i<8;i++)
		node->children[i] = 0;

	node->numberOfElements = 0;
	node->contentElements = idx;
	nodePool->ce_pool[idx] = (unsigned *) malloc(sizeof(unsigned)*OT_NODE_CAPACITY);
	
	nodePool->pool_idx += 1;

	return idx;
}


bool octreeInsertVertex(struct OctreeNode* node, unsigned idx, float *vertexPool, struct OctreePool* nodePool) {
	float   x = vertexPool[ idx*3 ],
			y = vertexPool[idx*3+1],
			z = vertexPool[idx*3+2];

	if (!(  fabs(x-node->center[0])<=node->radius[0] && 
			fabs(y-node->center[1])<=node->radius[1] && 
			fabs(z-node->center[2])<=node->radius[2]))
		return false;

	if (node->numberOfElements < OT_NODE_CAPACITY) {
		nodePool->ce_pool[node->contentElements][node->numberOfElements] = idx;
		node->numberOfElements++;
		return true;
	}
	else if (node->numberOfElements == OT_NODE_CAPACITY)
		octreeSubdivide(node, vertexPool, nodePool);
	
	node->numberOfElements++;

	bool	xaxis = x <= node->center[0],
			yaxis = y <= node->center[1],
			zaxis = z <= node->center[2];

	unsigned flag = 4*xaxis | 2*yaxis | zaxis;

	if (node->children[flag] == 0) {
		float radius[3], center[3];
		radius[0] = node->radius[0]/2;
		radius[1] = node->radius[1]/2;
		radius[2] = node->radius[2]/2;

		center[0] = node->center[0] + (xaxis ? -radius[0] : radius[0]);
		center[1] = node->center[1] + (yaxis ? -radius[1] : radius[1]);
		center[2] = node->center[2] + (zaxis ? -radius[2] : radius[2]);

		node->children[flag] = takeNodeFromPool(center, radius, nodePool);
	}

	return octreeInsertVertex(&nodePool->pool[node->children[flag]], idx, vertexPool, nodePool);
}


void octreeSubdivide(struct OctreeNode* node, float *vertexPool, struct OctreePool* nodePool) {
	unsigned i, flag, idx;
	bool xaxis, yaxis, zaxis;
	float radius[3], center[3];

	for (i=0; i<OT_NODE_CAPACITY; i++) {
		idx = nodePool->ce_pool[node->contentElements][i];
		xaxis = vertexPool[ idx*3 ] <= node->center[0];
		yaxis = vertexPool[idx*3+1] <= node->center[1];
		zaxis = vertexPool[idx*3+2] <= node->center[2];

		flag = 4*xaxis | 2*yaxis | zaxis;

		if (node->children[flag] == 0) {
			radius[0] = node->radius[0]/2;
			radius[1] = node->radius[1]/2;
			radius[2] = node->radius[2]/2;

			center[0] = node->center[0] + (xaxis ? -radius[0] : radius[0]);
			center[1] = node->center[1] + (yaxis ? -radius[1] : radius[1]);
			center[2] = node->center[2] + (zaxis ? -radius[2] : radius[2]);

			node->children[flag] = takeNodeFromPool(center, radius, nodePool);
		}

		octreeInsertVertex(&nodePool->pool[node->children[flag]], nodePool->ce_pool[node->contentElements][i], vertexPool, nodePool);
	}

	free(nodePool->ce_pool[node->contentElements]);
}


unsigned octreeRecursiveDefragment(struct OctreeNode *inNode,
	struct OctreePool* nodePool,
	unsigned *poolOffset,
	unsigned vertexIdxOffset,
	unsigned *vertexIdxPool,
	struct OctreeNode* swapNode,
	unsigned * childrenRefTMP) {

	if (inNode->numberOfElements <= OT_NODE_CAPACITY) {
		memcpy( vertexIdxPool+vertexIdxOffset,
				nodePool->ce_pool[inNode->contentElements],
				inNode->numberOfElements*sizeof(unsigned));

		free(nodePool->ce_pool[inNode->contentElements]);
	}

	else {
		unsigned i, tmp=vertexIdxOffset;
		for (i=0; i<8; i++)
			if (inNode->children[i] != 0) {
				memcpy(swapNode, nodePool->pool+(*poolOffset) , sizeof(struct OctreeNode));
				memcpy(nodePool->pool+(*poolOffset), nodePool->pool+childrenRefTMP[inNode->children[i]], sizeof(struct OctreeNode));
				memcpy(nodePool->pool+childrenRefTMP[inNode->children[i]], swapNode, sizeof(struct OctreeNode));

				childrenRefTMP[swapNode->contentElements] = childrenRefTMP[inNode->children[i]];

				inNode->children[i] = (*poolOffset)++;

				tmp += octreeRecursiveDefragment(   &nodePool->pool[inNode->children[i]], 
													nodePool, poolOffset, tmp, vertexIdxPool, 
													swapNode, childrenRefTMP);
			}
	}

	inNode->contentElements = vertexIdxOffset;

	return inNode->numberOfElements;
}


void octreeDefragment(struct OctreePool* nodePool, unsigned *vertexIdxPool) {
	unsigned * childrenRefTMP = (unsigned *) malloc(sizeof(unsigned)*nodePool->pool_idx);
	unsigned i;

	for (i=0; i<nodePool->pool_idx; i++)
		childrenRefTMP[i] = i;
	
	struct OctreeNode *swapNode = (struct OctreeNode *) malloc(sizeof(struct OctreeNode));
	unsigned poolOffset = 1;

	octreeRecursiveDefragment(nodePool->pool, nodePool, &poolOffset, 0, vertexIdxPool, swapNode, childrenRefTMP);

	free(swapNode);
	free(childrenRefTMP);
}


unsigned ROIsSegmentationPopulateAndDefragmentPool(void * pyOCPool,
	int octreePoolSize,
	void * pyPoints,
	int pointsSize,
	void * pyCenter,
	void * pyRadius,
	void * pyVertexIdxPool) {
	// Cast inputs
	float *points = (float*) pyPoints;
	float *center = (float*) pyCenter, *radius = (float*) pyRadius;
	unsigned *vertexIdxPool = (unsigned*) pyVertexIdxPool;

	// Build pool struct
	struct OctreePool nodePool;
	nodePool.pool = (struct OctreeNode*) pyOCPool;
	nodePool.pool_size = octreePoolSize;
	nodePool.pool_idx = 0;

	nodePool.ce_pool = (unsigned **) malloc(sizeof(unsigned*)*octreePoolSize);

	struct OctreeNode *root = &nodePool.pool[takeNodeFromPool(center, radius, &nodePool)];

	unsigned i;

	for (i=0;i<pointsSize/3;i++)
		octreeInsertVertex(root, i, points, &nodePool);

	octreeDefragment(&nodePool, vertexIdxPool);
	free(nodePool.ce_pool);

	return nodePool.pool_idx;
}


// Collision query


bool boundaryIntersectsSphere(struct ROI * sphere, struct OctreeNode * node) {
	float squaredDistPoint = 0;

	if(sphere->center[0] < node->center[0]-node->radius[0])
		squaredDistPoint += (sphere->center[0]-(node->center[0]-node->radius[0]))*(sphere->center[0]-(node->center[0]-node->radius[0]));
	else if(sphere->center[0] > node->center[0]+node->radius[0])
		squaredDistPoint += (sphere->center[0]-(node->center[0]+node->radius[0]))*(sphere->center[0]-(node->center[0]+node->radius[0]));

	if(sphere->center[1] < node->center[1]-node->radius[1])
		squaredDistPoint += (sphere->center[1]-(node->center[1]-node->radius[1]))*(sphere->center[1]-(node->center[1]-node->radius[1]));
	else if(sphere->center[1] > node->center[1]+node->radius[1])
		squaredDistPoint += (sphere->center[1]-(node->center[1]+node->radius[1]))*(sphere->center[1]-(node->center[1]+node->radius[1]));

	if(sphere->center[2] < node->center[2]-node->radius[2])
		squaredDistPoint += (sphere->center[2]-(node->center[2]-node->radius[2]))*(sphere->center[2]-(node->center[2]-node->radius[2]));
	else if(sphere->center[2] > node->center[2]+node->radius[2])
		squaredDistPoint += (sphere->center[2]-(node->center[2]+node->radius[2]))*(sphere->center[2]-(node->center[2]+node->radius[2]));

	return squaredDistPoint <= sphere->radius[0]*sphere->radius[0];
}


bool sphereContainsVertex(struct ROI * sphere, float vertex_x, float vertex_y, float vertex_z) {
	float x = vertex_x - sphere->center[0],
		  y = vertex_y - sphere->center[1],
		  z = vertex_z - sphere->center[2];

	return x*x + y*y + z*z <= sphere->radius[0]*sphere->radius[0];
}


bool SphereContainsBoundary(struct ROI * sphere, struct OctreeNode * node) {
	return (sphereContainsVertex(sphere, node->center[0]-node->radius[0], node->center[1]-node->radius[1], node->center[2]-node->radius[2]) &&
			sphereContainsVertex(sphere, node->center[0]+node->radius[0], node->center[1]-node->radius[1], node->center[2]-node->radius[2]) &&
			sphereContainsVertex(sphere, node->center[0]-node->radius[0], node->center[1]+node->radius[1], node->center[2]-node->radius[2]) &&
			sphereContainsVertex(sphere, node->center[0]-node->radius[0], node->center[1]-node->radius[1], node->center[2]+node->radius[2]) &&
			sphereContainsVertex(sphere, node->center[0]+node->radius[0], node->center[1]+node->radius[1], node->center[2]-node->radius[2]) &&
			sphereContainsVertex(sphere, node->center[0]+node->radius[0], node->center[1]-node->radius[1], node->center[2]+node->radius[2]) &&
			sphereContainsVertex(sphere, node->center[0]-node->radius[0], node->center[1]+node->radius[1], node->center[2]+node->radius[2]) &&
			sphereContainsVertex(sphere, node->center[0]+node->radius[0], node->center[1]+node->radius[1], node->center[2]+node->radius[2]));
}


void querySphere(struct ROI * sphere, int nodeIdx, struct OctreeNode * nodePool, unsigned * vertex2Fiber, unsigned * vertexIdxPool, float * points, bool * result) {
	struct OctreeNode * node = &nodePool[nodeIdx];
	unsigned i, vertex;

	if (!boundaryIntersectsSphere(sphere, node))
		return;

	if (SphereContainsBoundary(sphere, node)) {
		// memcpy(result+(*resultOffset), vertexIdxPool + node->contentElements, sizeof(unsigned)*node->numberOfElements);
		// (*resultOffset) += node->numberOfElements;
		for(i=0; i<node->numberOfElements; i++)
			result[vertex2Fiber[vertexIdxPool[node->contentElements+i]]] = true;
		return;
	}

	if (node->numberOfElements <= OT_NODE_CAPACITY)
		for (i=0; i<node->numberOfElements; i++) {
			vertex = 3*(vertexIdxPool[node->contentElements+i]);

			if (sphereContainsVertex(sphere, points[vertex], points[vertex+1], points[vertex+2]))
				// result[(*resultOffset)++] = vertexIdxPool[node->contentElements+i];
				result[vertex2Fiber[vertex/3]] = true;
		}

	else
		for (i=0; i<8; i++)
			if (node->children[i] != 0)
				querySphere(sphere, node->children[i], nodePool, vertex2Fiber, vertexIdxPool, points, result);
}


void queryTree(int nROI,
	void * pyROIDataArray,
	void * pyOCPool,
	void * pyVertexIdxPool,
	void * pyVertex2Fiber,
	void * pyPoints,
	void * pyResult,
	int curvesCount) {

	struct ROI * ROIDataArray = (struct ROI*) pyROIDataArray;
	struct OctreeNode * nodePool = (struct OctreeNode*) pyOCPool;
	unsigned * vertexIdxPool = (unsigned *) pyVertexIdxPool;
	unsigned * vertex2Fiber = (unsigned *) pyVertex2Fiber;
	float *points = (float*) pyPoints;
	bool * result = (bool *) pyResult;

	int i;

	for (i=0; i<nROI; i++) {

		switch(ROIDataArray[i].roiType) {

		// Sphere
		case 0:
			// printf("Query for sphere!\n");

			querySphere(&ROIDataArray[i], 0, nodePool, vertex2Fiber, vertexIdxPool, points, result+i*curvesCount);
			break;

		// // AABB
		// case 1:
		// 	printf("AABB query not implemented.\n");
		// 	break;

		// // OBB
		// case 2:
		// 	printf("OBB query not implemented.\n");
		// 	break;

		// // Plane
		// case 3:
		// 	printf("Plane query not implemented.\n");
		// 	break;

		// Not defined
		default:
			printf("ROIType not sopported: %i\n", ROIDataArray[i].roiType);
			break;
		}
	}
}


int createEBO(int curvesCount,
	void *pyFiberValidator,
	void *pyFiberSize,
	void *pyEbo,
	int end) {

	bool * fiberValidator = (bool *) pyFiberValidator;
	int *fiberSize = (int *) pyFiberSize;
	GLuint *ebo = (GLuint *) pyEbo;
	
	int eboSize = 0;
	int index = 0, begin = 0, i, j;
	end -= 1;

	for (i=0; i<curvesCount; i++) {
		if (fiberValidator[i]) {
			eboSize += fiberSize[i] + 1;

			for (j=0; j<fiberSize[i]; j++)
				ebo[begin++] = index++;
			ebo[begin++] = 0xFFFFFFFF;
		}
		else {
			for (j=0; j<fiberSize[i]; j++)
				ebo[end--] = index++;
			ebo[end--] = 0xFFFFFFFF;
		}
	}

	return eboSize; 
}


void ROISegmentationExportbundlesdata(char * filePath,
		int bundleN,
		void * pyBundlesStart,
		void * pyFiberSize,
		void * pyBundleCount,
		void * pyPoints,
		void * pyFiberValidator) {

	int * bundleStart = (int *) pyBundlesStart;
	int * fiberSize = (int *) pyFiberSize;
	int * bundleCount = (int *) pyBundleCount;
	float * points = (float *) pyPoints;
	bool * fiberValidator = (bool *) pyFiberValidator;

	// open bundledata file
	FILE *fp;
	fp = fopen(filePath, "wb");
	int i, j;

	for (i=0; i<bundleN; i++) {
		for (j=bundleStart[i]; j<bundleStart[i+1]; j++) {
			if (fiberValidator[j]) {
				bundleCount[i]++;
				fwrite(fiberSize+j, sizeof(int), 1, fp);
				fwrite(points, sizeof(GLfloat), fiberSize[j]*3, fp);
			}

			points += 3*fiberSize[j];
		}
	}

	fclose(fp);
}