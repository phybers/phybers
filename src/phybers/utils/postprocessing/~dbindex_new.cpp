/* main.cpp
   Authors:
   Narciso López López
   Andrea Vázquez Varela
   Last update: 15-02-2020 */

#include "dbindex.hpp"

using namespace std;

#define min(a, b) (((a) < (b)) ? (a) : (b))

void write_results(float val, vector<float> &intra_dists, vector<float> &sums, vector<float> &intra_meandists, vector<vector<float>> &inter_dists, string name)
{

    ofstream myfile;
    myfile.open(name + "_DBVal.txt");
    myfile << to_string(val);
    myfile.close();

    myfile.open(name + "_intra_max_dists.txt");
    for (int i = 0; i < intra_dists.size(); i++)
        myfile << to_string(i) << " " << to_string(intra_dists[i]) + "\n";
    myfile.close();

    myfile.open(name + "_Ri_db.txt");
    for (int i = 0; i < sums.size(); i++)
        myfile << to_string(i) << " " << to_string(sums[i]) + "\n";
    myfile.close();

    myfile.open(name + "_intra_means_dists.txt");
    for (int i = 0; i < intra_meandists.size(); i++)
        myfile << to_string(i) << " " << to_string(intra_meandists[i]) + "\n";
    myfile.close();

    myfile.open(name + "_inter_dists.txt");
    for (int i = 0; i < inter_dists.size(); i++)
    {
        float min_val = 1000;
        for (int j = 0; j < inter_dists[i].size(); j++)
        {
            float idist = inter_dists[i][j];
            if (idist != -1 && idist < min_val)
                min_val = idist;
        }
        myfile << to_string(i) << " " << to_string(min_val) + "\n";
    }

    myfile.close();
}

void write_results_2(float val, vector<float> &intra_dists, vector<float> &max_values, vector<float> &intra_meandists, vector<float> &min_values, string name)
{

    ofstream myfile;
    myfile.open(name + "_DBVal.txt");
    myfile << to_string(val);
    myfile.close();

    myfile.open(name + "_intra_max_dists.txt");
    for (int i = 0; i < intra_dists.size(); i++)
        myfile << to_string(i) << " " << to_string(intra_dists[i]) + "\n";
    myfile.close();

    myfile.open(name + "_Ri_db.txt");
    for (int i = 0; i < max_values.size(); i++)
        myfile << to_string(i) << " " << to_string(max_values[i]) + "\n";
    myfile.close();

    myfile.open(name + "_intra_means_dists.txt");
    for (int i = 0; i < intra_meandists.size(); i++)
        myfile << to_string(i) << " " << to_string(intra_meandists[i]) + "\n";
    myfile.close();

    myfile.open(name + "_inter_dists.txt");
    for (int i = 0; i < min_values.size(); i++)
    {
        myfile << to_string(i) << " " << to_string(min_values[i]) + "\n";
    }

    myfile.close();
}

char *str_to_char_array(string s)
{
    char *cstr = new char[s.length() + 1];
    strcpy(cstr, s.c_str());
    return cstr;
}

/*Read .bundles files and return (by reference) a vector with the datas*/
vector<float> read_bundles(string path, unsigned short int ndata_fiber)
{
    vector<float> data;
    char *path2 = (char *)malloc(sizeof(char) * (path.length() + 1));
    strncpy(path2, path.c_str(), (path.length() + 1));
    path2[path.length()] = 0;
    FILE *fp = fopen(path2, "rb");
    // Open subject file.
    if (fp == NULL)
    {
        fputs("File error opening file\n", stderr);
        exit(1);
    }
    fseek(fp, 0, SEEK_END);
    long lSize = ftell(fp);                                               // Get file size.
    unsigned int sfiber = sizeof(uint32_t) + ndata_fiber * sizeof(float); // Size of a fiber (bytes).  // Add 1 element (uint32_t) because in .bundles/.bundlesdata format the first element of each fiber/centroid corresponds to the amount of points in the fiber/centroid. In this case that number should be always the same.
    float *buffer = (float *)malloc(sizeof(float) * sfiber);
    unsigned int nFibers = lSize / (float)sfiber; // Number of fibers
    rewind(fp);
    for (unsigned int j = 0; j < (nFibers); ++j) // Copy fibers.
    {
        int r = fread(buffer, sizeof(float), (ndata_fiber + 1), fp); // Skip the first element of each fiber/centroid (number of points).;
        if (r == -1)
            cout << "error reading buffer data";
        for (int s = 1; s < ndata_fiber + 1; ++s)
        {
            data.push_back(buffer[s]);
        }
    }

    fclose(fp);
    free(buffer);
    free(path2);
    return data;
}

vector<string> get_bundle_files(string path)
{
    DIR *dpdf;
    struct dirent *epdf;
    vector<string> files;
    vector<int> sort_files;
    char *path_char = str_to_char_array(path + "/");
    dpdf = opendir(path_char);
    while (epdf = readdir(dpdf))
    {
        string name = (epdf->d_name);
        size_t lastindex = name.find_last_of(".");
        string rawname = name.substr(0, lastindex);
        string ext = name.substr(lastindex, name.length());
        if (ext.compare(".bundles") == 0)
        {
            int int_val = 0;
            stringstream name(rawname);
            name >> int_val;
            sort_files.push_back(int_val);
        }
    }
    sort(sort_files.begin(), sort_files.end());
    closedir(dpdf);
    for (int i = 0; i < sort_files.size(); i++)
    {
        stringstream ss;
        ss << sort_files[i];
        string s;
        ss >> s;
        files.push_back(s + ".bundles");
    }
    return files;
}

float sqrt7(float x)
{
    unsigned int i = *(unsigned int *)&x;
    i += 127 << 23; // adjust bias
    i >>= 1;        // approximation of square root
    return *(float *)&i;
}

/*Calculate the euclidean distance between two 3d points normalized*/
float euclidean_distance_norm(float x1, float y1, float z1, float x2, float y2, float z2)
{
    return sqrt7((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2) + (z1 - z2) * (z1 - z2));
}

float euclidean_21points_mean(vector<float> &bundle_data, unsigned int fiber_index1, unsigned int fiber_index2, short int ndata_fiber)
{
    unsigned short int inv = 20;
    float avg_direct = 0;
    float avg_inv = 0;
    for (unsigned short int i = 0; i < 21; i++)
    {
        unsigned int fiber_point = (ndata_fiber * fiber_index1) + (i * 3);
        unsigned int atlas_point = (ndata_fiber * fiber_index2) + (i * 3);
        unsigned int point_inv = (ndata_fiber * fiber_index2) + (inv * 3);

        avg_direct += euclidean_distance_norm(bundle_data[fiber_point], bundle_data[fiber_point + 1], bundle_data[fiber_point + 2],
                                              bundle_data[atlas_point], bundle_data[atlas_point + 1], bundle_data[atlas_point + 2]);
        avg_inv += euclidean_distance_norm(bundle_data[fiber_point], bundle_data[fiber_point + 1], bundle_data[fiber_point + 2],
                                           bundle_data[point_inv], bundle_data[point_inv + 1], bundle_data[point_inv + 2]);

        inv--;
    }

    avg_direct = avg_direct / 21;
    avg_inv = avg_inv / 21;
    return (min(avg_direct, avg_inv));
}

float euclidean_21points_max(vector<float> &bundle_data, unsigned int fiber_index1, unsigned int fiber_index2, short int ndata_fiber)
{
    unsigned short int inv = 20;
    float max_direct = 0;
    float max_inv = 0;
    for (unsigned short int i = 0; i < 21; i++)
    {
        unsigned int fiber_point = (ndata_fiber * fiber_index1) + (i * 3);
        unsigned int atlas_point = (ndata_fiber * fiber_index2) + (i * 3);
        unsigned int point_inv = (ndata_fiber * fiber_index2) + (inv * 3);

        float ed_direct = euclidean_distance_norm(bundle_data[fiber_point], bundle_data[fiber_point + 1], bundle_data[fiber_point + 2],
                                                  bundle_data[atlas_point], bundle_data[atlas_point + 1], bundle_data[atlas_point + 2]);
        float ed_inv = euclidean_distance_norm(bundle_data[fiber_point], bundle_data[fiber_point + 1], bundle_data[fiber_point + 2],
                                               bundle_data[point_inv], bundle_data[point_inv + 1], bundle_data[point_inv + 2]);

        inv--;

        if (ed_direct > max_direct)
            max_direct = ed_direct;
        if (ed_inv > max_inv)
            max_inv = ed_inv;
    }

    return (min(max_direct, max_inv));
}

float intra_dist_mean(vector<float> &fibers, unsigned short int ndata_fiber)
{
    int nFibers = fibers.size() / ndata_fiber;
    float avg_dist = 0;
    int count = 0;
    for (unsigned int i = 0; i < nFibers; i++)
    {
        for (unsigned int j = 0; j < nFibers; j++)
        {
            if (i != j)
            {
                avg_dist += euclidean_21points_max(fibers, i, j, ndata_fiber);
                count += 1;
            }
        }
    }
    return (avg_dist / count);
}

float intra_dist_max(vector<float> &fibers, unsigned short int ndata_fiber)
{
    int nFibers = fibers.size() / ndata_fiber;
    float max_dist = 0;
    for (unsigned int i = 0; i < nFibers; i++)
    {
        for (unsigned int j = 0; j < nFibers; j++)
        {
            if (i != j)
            {
                float dist = euclidean_21points_max(fibers, i, j, ndata_fiber);
                if (dist > max_dist)
                    max_dist = dist;
            }
        }
    }
    return (max_dist);
}

struct max_mean_pair intra_dist_max_mean(vector<float> &fibers, unsigned short int ndata_fiber)
{
    unsigned int i, j;
    unsigned int nFibers = fibers.size() / ndata_fiber;
    float dist;
    struct max_mean_pair dist_mm = {-1, 0};
    double max_mean_dist;
    for(i = 0; i < nFibers; i++){
        for(j = 0; j < nFibers; j++){
            dist = euclidean_21points_max(fibers, i, j, ndata_fiber);
            dist_mm.mean += dist;
            if (dist > dist_mm.max) dist_mm.max = dist;
        }
    }
    dist_mm.mean /= (nFibers * (nFibers - 1));
    return dist_mm;
}

    int main(int argc, char *argv[])
{

    unsigned t0, t1;

    t0 = clock();

    string centroids_path = argv[1];
    string bundles_path = argv[2];
    string name = argv[3];

    unsigned short int npoints = atoi(argv[4]);
    unsigned short int ndata_fiber = npoints * 3;

    vector<float> centroids_data = read_bundles(centroids_path + "data", ndata_fiber);
    vector<string> bfiles = get_bundle_files(bundles_path);

    unsigned int nunProc = omp_get_num_procs();
    omp_set_num_threads(nunProc);

    bfiles.erase(bfiles.cbegin() + 1000, bfiles.cend());
    centroids_data.erase(centroids_data.cbegin() + 63000, centroids_data.cend());

    int n = bfiles.size();
    vector<float> intra_dists(n);
    vector<float> intra_meandists(n);

    vector<vector<float>> all_bundles;
    for (int i = 0; i < n; i++)
    {
        all_bundles.push_back(read_bundles(bundles_path + "/" + bfiles[i] + "data", ndata_fiber));

    }

    struct max_mean_pair dist_max_mean;
    #pragma omp parallel
    {
    #ifdef _MSC_VER
        #pragma omp for schedule(runtime) nowait
    #else
        #pragma omp for schedule(auto) nowait
    #endif
        for (int i = 0; i < bfiles.size(); i++)
        {
            dist_max_mean = intra_dist_max_mean(all_bundles[i], ndata_fiber);
            intra_dists[i] = dist_max_mean.max;
            intra_meandists[i] = dist_max_mean.mean;
/*             float dist = intra_dist_max(all_bundles[i], ndata_fiber);
            intra_dists[i] = dist;
            float meansdist = intra_dist_mean(all_bundles[i], ndata_fiber);
            intra_meandists[i] = meansdist; */
        }
    }

    // vector<float> sums(n);
    // Cuidado con el tam, puede faltar memoria ya que es matriz cuadrada
    // vector<vector<float>> inter_dists(n, vector<float>(n, -1));
    float inter_dist, intra_dist_i, intra_dist_j, max_value, min_dist, value;
    vector<float> mins(n), maxs(n);

    #pragma omp parallel
    {
        #ifdef _MSC_VER
            #pragma omp for schedule(runtime) nowait
        #else
            #pragma omp for schedule(auto) nowait
        #endif
        for (int i = 0; i < bfiles.size(); i++)
        {
            intra_dist_i = intra_dists[i];
            max_value = -1.0;
            min_dist = 0x1.p127;
            // float max = -1;
            for (int j = 0; j < bfiles.size(); j++)
            {
                if (i != j)
                {
                    intra_dist_j = intra_dists[j];
                    inter_dist = euclidean_21points_max(centroids_data, i, j, ndata_fiber);
                    // inter_dists[i][j] = inter_dist;
                    if ((inter_dist > 0) && (intra_dist_i > 0) && (intra_dist_j > 0))
                    {
                        value = ((intra_dist_i + intra_dist_j)) / inter_dist;
                        if (value > max_value)
                            max_value = value;
                        if (inter_dist < min_dist)
                            min_dist = inter_dist;
                    }
                    // if (value > max) max = value;
                }
            }
            maxs[i] = max_value;
            mins[i] = min_dist;
            // sums[i] = max;
        }
    }
    float max_sum = 0.0;
    for (int i = 0; i < maxs.size(); i++)
        max_sum += maxs[i];

    // write_results(DBval, intra_dists, sums, intra_meandists, inter_dists, name);
    write_results_2(max_sum / n, intra_dists, maxs, intra_meandists, mins, name);

    t1 = clock();

    double time = (double(t1 - t0) / CLOCKS_PER_SEC);
    cout << "Execution Time: " << time << endl;

    return 0;
}
