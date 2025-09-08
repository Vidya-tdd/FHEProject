import tenseal as ts


def fetch_data(df):
    print(df.head())
    v3 = df['Amount'].values.flatten()
    print(v3)
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
    v4 = [10.10, 20.10, 30.10, 40.10]

    # encrypted vectors
    enc_v1 = ts.ckks_vector(context, v1)
    enc_v2 = ts.ckks_vector(context, v2)
    enc_v3 = ts.ckks_vector(context, vector)
    enc_v4 = ts.ckks_vector(context, v4)


    #addition of data point float
    resultData= enc_v3 + enc_v4
    ultimate_result_float = resultData.decrypt()
    print(ultimate_result_float)


    #addition
    result = enc_v1 + enc_v2
    result_add = result.decrypt() # ~ [4, 4, 4, 4, 4]
    print(result_add)


    #multiplication
    result = enc_v1 * enc_v2
    result_multiply = result.decrypt() # ~ [4, 4, 4, 4, 4]
    print(result_multiply)

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

