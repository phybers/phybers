#include "distances.hpp"

#define IDXK_SIZE 1024 * 1024

int fDM_main(char *fp_input, char *fp_output)
{
    struct bundle f1;
    f1 = read_bundle(fp_input);

    float **m = fiberDistanceMax(f1);

    FILE *fw;
    fw = fopen(fp_output, "wb");

    int i, j, cont = 1;
    for (i = 0; i < f1.nfibers; i++)
    {
        for (j = 0; j < f1.nfibers; j++)
        {
            if (j < cont)
            {
                fprintf(fw, "%f\t", sqrt(*(m[i] + j)));
            }
            else
            {
                fprintf(fw, "%f\t", sqrt(*(m[j] + i)));
            }
            if (j == f1.nfibers - 1)
            {
                fprintf(fw, "\n");
            }
        }
        cont++;
    }

    fclose(fw);
    free_bundle(f1);
    return 0;
}

int gAGFDM_main(char *fp_input, char *fp_output, float maxdist)
{
    clock_t t_start = clock(); // medir tiempo ejecución

    float var = 3600.;             // varianza

    std::vector<std::vector<double>> matrix_distance; // matriz que almacena las distancias
    std::vector<double> v;                       // std::vector para leer la entrada binaria del fichero y pasar posteriormente a la matriz de distancias

    std::ifstream in(fp_input, std::ios_base::in); // fichero binario de entrada con las distancias de las fibras

    if (!in.is_open())
    { // comprobación para saber si se ha abierto el fichero
        std::cout << "Error opening file";
        exit(1);
    }

    std::string str;
    while (getline(in, str))
    { // leer linea a linea el fichero binario de entrada
        std::istringstream ss(str);
        double num;
        while (ss >> num)
            v.push_back(num);         // insertar al std::vector
        matrix_distance.push_back(v); // insertar a la matriz de distancias
        v.clear();
    }

    in.close(); // se cierra el fichero binario de entrada

    float dist, aff = 0.;
    unsigned int nodes = 0;          // contador para saber el número de nodos
    unsigned int edges = 0;          // contador para saber el número de aristas
    FILE *out = fopen(fp_output, "w"); // ruta del fichero de salida para almacenar el "grafo de afinidades"

    fprintf(out, "%s", "                     \n"); // dejar espacio para introducir nodes y edges a posteriori

    for (unsigned int p1 = 0; p1 < matrix_distance.size(); p1++)
    {
        for (unsigned int p2 = 0; p2 < p1; p2++)
        {                                   // se recorre como si fuera una triangular inferior ya que por simetría no es necesario hacer todas las operaciones
            dist = matrix_distance[p1][p2]; // obtener distancia de la celda entre nodos
            if (dist <= maxdist)
            {                                            // si la distancia entre nodos es más pequeña que la distancia del clúster
                aff = exp(-dist * dist / var);           // cálculo de la afinidad entre nodos
                fprintf(out, "%d %d %f\n", p2, p1, aff); // escribir conexiones entre nodos y afinidad entre ellos
                fprintf(out, "%d %d %f\n", p1, p2, aff);
                edges += 2; // número de aristas +2
            }
        }
        nodes++; // número de nodos +1
    }

    rewind(out);                         // inicio de fichero
    fprintf(out, "%d %d", nodes, edges); // escribir número de nodos y aristas
    fclose(out);                         // cerrar fichero de salida

    //   std::cout << "Execution Time: " << ((double)(clock() - t_start)*1000)/CLOCKS_PER_SEC  << " ms" << std::endl;	// mostrar tiempo de ejecución
    std::cout << "Execution Time: " << ((double)(clock() - t_start)) / CLOCKS_PER_SEC << " secs" << std::endl; // mostrar tiempo de ejecución

    return EXIT_SUCCESS;
}

struct smax floatmax(std::vector<float> &dvector, int lenght)
{
    int i;
    struct smax sm;
    sm.value = dvector[0];
    sm.arg = 0;
    for (i = 1; i < lenght; i += 1)
    {
        if (dvector[i] > sm.value)
        {
            sm.value = dvector[i];
            sm.arg = i;
        }
    }
    return sm;
}

int gALHCFGF_main(char *fp_input, char *fp_output)
{
    static std::vector<int> corr;
    static std::vector<int> acorr;
    static std::vector<int> scorr;

    struct
    {
        bool operator()(int a, int b)
        {
            return corr[a] < corr[b];
        }
    } customLess;

    // sort(scorr.begin(), scorr.begin(), comp);
    // sort(acorr.begin(), acorr.end(), compind);

    std::vector<int> edges[2];
    std::vector<float> weights;
    std::vector<float> height;
    std::vector<int> pop;
    std::vector<int> cc;
    std::vector<int> father;
    std::vector<int> idxk(IDXK_SIZE, 0);

    clock_t t_start = clock();

    int nV, nE = 0;
    int maxv = 0;

    std::ifstream is(fp_input);

    if (is.fail())
    {
        std::cout << "Fail" << std::endl
             << std::flush;
        return EXIT_FAILURE;
    }
    std::cout << "File Opened" << std::endl
            << std::flush;
    is >> nV;
    is >> nE;
    std::cout << "Edges: " << nE
            << " Vertices: " << nV << std::endl
            << std::flush;

    maxv = 2 * nV;
    edges[0].resize(nE);
    edges[1].resize(nE);
    weights.resize(2 * nE);
    height.resize(maxv);
    father.resize(maxv);
    pop.resize(maxv);

    for (int i = 0; i < maxv; i += 1)
    {
        pop[i] = 1;
        height[i] = INT_MAX;
        father[i] = i;
    }
    ///////////////////////////////////////////

    // Read
    for (int i = 0; i < nE; i += 1)
    {
        is >> edges[0][i];
        is >> edges[1][i];
        is >> weights[i];
    }

    // CONNECTED COMPONENTS
    int n1, ne;
    int k;
    int remain = nV;
    int su, sv;
    cc.resize(nV);

    for (n1 = 0; n1 < nV; n1++)
        cc[n1] = -1;

    k = 0;
    while (remain > 0)
    {
        n1 = 0;
        while (cc[n1] > -1)
            n1++;
        cc[n1] = k;
        su = 0;
        sv = 1;

        while (sv > su)
        {
            su = sv;
            for (ne = 0; ne < nE; ne++)
            {
                if (cc[edges[0][ne]] == k)
                    cc[edges[1][ne]] = k;
                if (cc[edges[1][ne]] == k)
                    cc[edges[0][ne]] = k;
            }
            sv = 0;
            for (n1 = 0; n1 < nV; n1++)
                sv += (cc[n1] == k);
        }

        remain = remain - su;
        k++;
    }

    int nbcc = k; // 0;
    // nbcc = k;
    maxv = maxv - nbcc;

    printf("Connected components: %d\n", nbcc);
    // fclose(inFile);

    // execute clustering
    //  AVERAGE_LINK()

    // std::vector<int> idxk[IDXK_SIZE]; // <--- STACK OVERFLOW CULPRIT
    k = 0;
    int m, q, j, i, a, p, i1, i2;
    float fi, fj;

    for (q = 0; q < nV - nbcc; q += 1)
    {
        if (q % 500 == 0)
        {
            printf("#");
            fflush(stdout);
        }
        // # 1. find the heaviest edge
        m = floatmax(weights, nE).arg; // best fitting edge
        k = q + nV;
        height[k] = weights[m]; // cost
        i = edges[0][m];        // element i from m edge
        j = edges[1][m];        // element j from m edge

        // # 2. remove the current edge
        edges[0][m] = -1;     // remove the m edge (the heaviest)
        edges[1][m] = -1;     // remove the m edge (the heaviest)
        weights[m] = INT_MIN; // delete its weight
        //   i,j what is this?...the other one? I sould't be reading clones...
        for (a = 0; a < nE; a += 1)
        {
            if ((edges[0][a] == j) && (edges[1][a] == i))
            {
                edges[0][a] = -1;
                edges[1][a] = -1;
                weights[a] = INT_MIN;
            }
            if ((edges[0][a] == i) && (edges[1][a] == j))
            {
                edges[0][a] = -1;
                edges[1][a] = -1;
                weights[a] = INT_MIN;
            }
        }
        // 3. merge the edges with third part edges
        father[i] = k;
        father[j] = k;
        pop[k] = pop[i] + pop[j];
        fi = ((float)pop[i]) / (pop[k]); // float
        fj = 1.0 - fi;

        // # replace i by k
        for (a = 0; a < nE; a += 1)
        {
            if (edges[0][a] == i)
            {
                weights[a] = weights[a] * fi;
                edges[0][a] = k;
            }
            if (edges[1][a] == i)
            {
                weights[a] = weights[a] * fi;
                edges[1][a] = k;
            }
            if (edges[0][a] == j)
            {
                weights[a] = weights[a] * fj;
                edges[0][a] = k;
            }
            if (edges[1][a] == j)
            {
                weights[a] = weights[a] * fj;
                edges[1][a] = k;
            }
        }

        // #sum/remove float edges
        //  #left side
        p = 0;
        for (a = 0; a < nE; a += 1)
        {
            if (edges[0][a] == k)
            {
                idxk[p++] = a; // catch every index with an k on the leftside
                if (p >= IDXK_SIZE)
                {
                    printf("idxk out of bounds\n");
                    break;
                }
            }
        }

        // std::cout << p << std::endl;

        // maybe the edges will need to be sorted...maybe not

        corr.resize(p);
        scorr.resize(p);
        acorr.resize(p);
        for (a = 0; a < p; a++)
        {
            corr[a] = edges[1][idxk[a]];
            scorr[a] = edges[1][idxk[a]];
            acorr[a] = a;
        }

        sort(scorr.begin(), scorr.begin());
        sort(acorr.begin(), acorr.end(), customLess);

        for (a = 0; a < p - 1; a += 1)
        {
            if (scorr[a] == scorr[a + 1])
            {
                i1 = idxk[acorr[a]];
                i2 = idxk[acorr[a + 1]];
                weights[i1] = weights[i1] + weights[i2];
                weights[i2] = INT_MIN;
                edges[0][i2] = -1;
                edges[1][i2] = -1;
            }
        }
        corr.clear();
        std::vector<int>().swap(corr);
        scorr.clear();
        std::vector<int>().swap(scorr);
        acorr.clear();
        std::vector<int>().swap(acorr);

        // #right side
        p = 0;
        for (a = 0; a < nE; a += 1)
        {
            if (edges[1][a] == k)
            {
                idxk[p++] = a; // catch every index with an k on the leftside
                if (p >= IDXK_SIZE)
                {
                    printf("idxk out of bounds\n");
                    break;
                }
            }
        }

        // maybe the edges will need to be sorted...maybe not
        corr.resize(p);
        scorr.resize(p);
        acorr.resize(p);
        for (a = 0; a < p; a += 1)
        {
            corr[a] = edges[0][idxk[a]];
            scorr[a] = edges[0][idxk[a]];
            acorr[a] = a;
        }

        sort(scorr.begin(), scorr.end());
        sort(acorr.begin(), acorr.end(), customLess);

        for (a = 0; a < p - 1; a += 1)
        {
            if (scorr[a] == scorr[a + 1])
            {
                i1 = idxk[acorr[a]];
                i2 = idxk[acorr[a + 1]];
                weights[i1] = weights[i1] + weights[i2];
                weights[i2] = INT_MIN;
                edges[0][i2] = -1;
                edges[1][i2] = -1;
            }
        }

        for (i = 0; i < maxv; i += 1)
        {
            if (height[i] < 0)
                height[i] = 0;
            if (height[i] == INT_MAX)
                height[i] = height[nV] + 1;
        }
    }

    int V = maxv;

    // initialize children std::vectors
    std::vector<int> _ch0(V, -1);
    std::vector<int> _ch1(V, -1);

    int fa;
    // determine children
    for (int i = 0; i < V; i++)
    {
        fa = father[i];
        // std::cout << "fa vale: " << fa << std::endl;
        // std::cout << "i vale: " << i << std::endl;
        if (fa != i)
        {
            if (_ch0[fa] == -1)
                _ch0[fa] = i;
            else
                _ch1[fa] = i;
        }
    }

    std::ofstream wforestFile;
    std::cout << fp_output << std::endl;
    wforestFile.open(fp_output);

    if (wforestFile)
    {
        wforestFile << maxv << std::endl;
        for (int i = 0; i < maxv; i++)
        {
            wforestFile << father[i] << " " << _ch0[i] << " " << _ch1[i] << std::endl;
        }
    }
    wforestFile.close();

    std::cout << "Execution Time: " << ((double)(clock() - t_start)) / CLOCKS_PER_SEC << " secs" << std::endl;
    std::cout << "done" << std::endl
         << std::flush;

    return EXIT_SUCCESS;
}