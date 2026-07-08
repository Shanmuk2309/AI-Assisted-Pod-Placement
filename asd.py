import ray

ray.init(address="ray://localhost:10001")

print(ray.cluster_resources())