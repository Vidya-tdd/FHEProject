import tenseal as ts


def fetch_data(df):
    print(df.head())
    v3 = df.values.flatten()
    return v3

def setup_tenseal(vector):
    # Setup TenSEAL context
    context = ts.context(
                ts.SCHEME_TYPE.CKKS,
                poly_modulus_degree=8192,
                coeff_mod_bit_sizes=[60, 40, 40, 60]
              )
    context.generate_galois_keys()
    context.global_scale = 2**40

    v1 = [0, 1, 2, 3, 4]
    v2 = [4, 3, 2, 1, 0]
    v3 = [200, 1.01]
    # Filter numeric values only
    numeric_values_v4 = [float(x) for x in vector if isinstance(x,(int,float)) or str(x).replace('.', '', 1).isdigit()]
    print(numeric_values_v4)

    # encrypted vectors
    enc_v1 = ts.ckks_vector(context, v1)
    enc_v2 = ts.ckks_vector(context, v2)
    enc_v3 = ts.ckks_vector(context, v3)
    enc_v4 = ts.ckks_vector(context, numeric_values_v4)

    #addition of data point float
    resultData= enc_v3.add(enc_v4)
    resultData.decrypt()
    print(resultData)


    #addition
    result = enc_v1 + enc_v2
    result.decrypt() # ~ [4, 4, 4, 4, 4]
    print(result)


    #multiplication
    result = enc_v1 * enc_v2
    result.decrypt() # ~ [4, 4, 4, 4, 4]
    print(result)

    result = enc_v1.dot(enc_v2)
    result.decrypt() # ~ [10]

    matrix = [
      [73, 0.5, 8],
      [81, -5, 66],
      [-100, -78, -2],
      [0, 9, 17],
      [69, 11 , 10],
    ]
    result = enc_v1.matmul(matrix)
    result.decrypt() # ~ [157, -90, 153]

