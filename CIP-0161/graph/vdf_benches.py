import secrets
import time
from statistics import stdev
from tabulate import tabulate

from chiavdf import create_discriminant, prove, verify_wesolowski


def bench_prove_and_verify():
    discriminant_challenge = secrets.token_bytes(10)

    discriminant_sizes = [256, 512, 1024]
    iterations = [100_000, 200_000, 500_000, 1_000_000, 2_000_000, 5_000_000, 10_000_000]
    benches = 100
    table = []

    for d in discriminant_sizes:
        for iters in iterations:
            res_prove = []
            res_verify = []
            for b in range(benches):
                discriminant = create_discriminant(discriminant_challenge, d)
                form_size = 100
                initial_el = b"\x08" + (b"\x00" * 99)

                t1 = time.time()
                result = prove(discriminant_challenge, initial_el, d, iters, "")
                t2 = time.time()
                res_prove.append(t2-t1)
                result_y = result[:form_size]
                proof = result[form_size : 2 * form_size]

                tv_1 = time.time()
                is_valid = verify_wesolowski(
                    str(discriminant),
                    initial_el,
                    result_y,
                    proof,
                    iters,
                )
                tv_2 = time.time()
                res_verify.append(tv_2 - tv_1)
                assert is_valid
            proving_time =  "{:.2E}".format(sum(res_prove)/len(res_prove))
            proving_deviation = "{:.2E}".format(stdev(res_prove))
            ips = "{:_.3f}".format(iters /  (sum(res_prove) / len(res_prove)))
            verification_time = "{:.2E}".format(1000 *(sum(res_verify)/len(res_verify)))
            verification_deviation = "{:.2E}".format(1000 * stdev(res_verify))
            table.append([d, ips, proving_time, proving_deviation, verification_time, verification_deviation ])
    headers = ["Size Discriminant", "IPS", "Proving time (s)", "σ proving", "Verification time (ms)", "σ verification"]
    print(tabulate(table, headers, tablefmt='orgtbl'))

bench_prove_and_verify()
