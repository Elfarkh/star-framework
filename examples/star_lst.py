landsat = Landsat()
sentinel3 = Sentinel3()

dataset = STARDataset(
    coarse_lst=...,
    fine_ndvi=...,
    reference_lst=...,
)

prepared = prepare(dataset)

geometry = build_triangle_geometry(prepared)

triangles = assign_samples(
    prepared,
    geometry,
)

regression = fit_regressions(triangles)

prediction = predict(regression)