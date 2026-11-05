
import detector
import stylometry

samples = {
    "sample_1": (
        "I enjoy programming. Sometimes it gets frustrating! "
        "But when everything finally works, it's worth it."
    ),
    "sample_2": (
        "The system provides an efficient and reliable solution "
        "for managing information. It improves productivity "
        "and supports users through a structured approach."
    ),
    "sample_3": (
        "I woke up late yesterday. Again! I rushed out of "
        "the house without breakfast, and then realized "
        "I had forgotten my keys."
    )
}

for name, text in samples.items():
    model = detector.model_signal(text)
    style = stylometry.style_signal(text)

    print(f"\n{name}")
    print(f"  Model score: {model:.4f}")
    print(f"  Style score: {style:.4f}")
    print(f"  Difference:  {abs(model - style):.4f}")
