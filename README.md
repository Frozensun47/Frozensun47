<h1 align="center">Hi, I'm Sagar Srivastava 👋</h1>

<p align="center">
  <a href="https://sagar-srivastava.com">
    <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=22&duration=3200&pause=900&color=58A6FF&center=true&vCenter=true&width=640&lines=Computer+Vision+%2F+ML+Engineer+%40+GolfWiz.ai;Vision+Transformers%2C+pose+estimation%2C+video+at+scale;FastAPI+%2B+Kubernetes+%2B+AWS+in+production;IIT+(BHU)+Varanasi+%2724" alt="Typing SVG" />
  </a>
</p>

<p align="center">
  <a href="https://sagar-srivastava.com"><img src="https://img.shields.io/badge/Portfolio-000000?style=for-the-badge&logo=google-chrome&logoColor=white" /></a>
  <a href="https://linkedin.com/in/sagar-srivastavaa"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" /></a>
  <a href="mailto:sagar.sriv.47@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" /></a>
  <img src="https://komarev.com/ghpvc/?username=Frozensun47&style=for-the-badge&color=58A6FF&label=PROFILE+VIEWS" />
</p>

---

I build **end-to-end computer vision systems** — from training custom Vision Transformers to running them behind autoscaling Kubernetes clusters. Right now I lead the backend and AI architecture for a professional-grade golf swing analysis platform.

- 🏌️ **Currently** — CV/ML Engineer at [GolfWiz.ai](https://golfwiz.ai), owning the analysis pipeline end to end
- 🔬 **Research** — Arbitrary-shaped scene text detection (87.6% F-score) and GANs for facial de-identification at IIT (BHU)
- 🎨 **Previously** — KeshcutAI: virtual try-on with Stable Diffusion + LoRA and template-based pose alignment
- 📫 **Reach me** — [sagar.sriv.47@gmail.com](mailto:sagar.sriv.47@gmail.com)

---

## 🏌️ What I'm building at GolfWiz.ai

> Most of my day-to-day work lives in the private [`golfwiz-ai`](https://github.com/golfwiz-ai) org, so it won't show up as public repos. What follows is the shape of the system I work on. The volume behind it is visible in the contribution graph below — private contributions included.

A single uploaded swing video fans out through a chain of services I designed and maintain:

```mermaid
flowchart LR
    A[📱 iOS / Android<br/>capture] --> B[Analysis Server<br/>FastAPI]
    B --> C[Camera Placement<br/>Classifier]
    C --> D[Pose Estimation<br/>ViTPose]
    D --> E[Phase Estimator<br/>swing segmentation]
    E --> F[Error Detector<br/>fault classification]
    E --> G[Swing Tracer<br/>club path overlay]
    E --> H[Rhythm / Tempo]
    F --> I[(PostgreSQL)]
    G --> I
    H --> I
    I --> J[Coach + Player<br/>Dashboard]
    B -.-> K[Anonymizer<br/>face / text redaction]

    style A fill:#1f6feb,stroke:#58a6ff,color:#fff
    style B fill:#238636,stroke:#3fb950,color:#fff
    style I fill:#8957e5,stroke:#a371f7,color:#fff
    style J fill:#1f6feb,stroke:#58a6ff,color:#fff
    style K fill:#6e7681,stroke:#8b949e,color:#fff
```

<details>
<summary><b>🧠 The ML services</b> — click to expand</summary>

<br/>

| Service | What it does |
| :--- | :--- |
| **Phase Estimator** | Segments a swing into its canonical phases (address → takeaway → top → impact → follow-through) so every downstream model reasons over aligned frames. |
| **Error Detector** | Multi-label fault classification against a structured error taxonomy — the model behind the coaching feedback users actually read. |
| **Swing Tracer** | Frame-accurate club-head tracking and path overlay rendered back onto the source video. |
| **Rhythm & Tempo** | Derives backswing:downswing ratios and tempo metrics from phase boundaries. |
| **Camera Placement Classifier** | Gates the pipeline early — rejects unusable angles before expensive inference runs. |
| **ViTPose (adapted)** | Pose backbone tuned for golf-specific keypoints, including a custom hip-keypoint training set. |
| **Anonymizer** | Privacy-first face/text/shaft redaction for videos used in training and research. |

</details>

<details>
<summary><b>⚙️ The platform underneath</b> — click to expand</summary>

<br/>

- **Serving** — FastAPI services on Kubernetes, split between a production server and a dedicated analysis fleet so heavy inference never blocks the API
- **CD** — GitOps-driven continuous delivery into the production cluster
- **Data** — PostgreSQL schema and models shared across services as a versioned submodule
- **Testing** — a dedicated pytest suite mounted into the server as a submodule
- **Clients** — native iOS and Android apps, plus web tools for grip classification, stance correction, and swing sharing
- **Internal tooling** — an annotators' dashboard and grip annotator that keep the training-data loop turning

</details>

<details>
<summary><b>📊 Where my commits actually go</b> — click to expand</summary>

<br/>

Last 12 months, by repository — the long tail of a system you own end to end:

```text
Server_Production   ████████████████████████████  1279
Server              █████████                      405
Error_Detector      ████████                       388
Server_utils        ██████                         271
Swing_Tracer        ████                           204
Phase_Estimator     ████                           184
golfwiz_android     ███                            158
Dashboard-frontend  ███                            151
Dashboard-server    ███                            137
db                  █                               81
golfwiz-ios-app     █                               72
models              ░                               35
```

</details>

---

## 🛠 Tech Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,pytorch,tensorflow,opencv,fastapi,docker,kubernetes,aws,postgres,redis&theme=dark" />
  <br/>
  <img src="https://skillicons.dev/icons?i=js,ts,react,nextjs,swift,kotlin,git,github,grafana,linux&theme=dark" />
</p>

<details>
<summary><b>Full breakdown</b></summary>

<br/>

**ML & Computer Vision**
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![Keras](https://img.shields.io/badge/Keras-D00000?style=flat-square&logo=keras&logoColor=white)
![ONNX](https://img.shields.io/badge/ONNX-005CED?style=flat-square&logo=onnx&logoColor=white)
![Hugging Face](https://img.shields.io/badge/HuggingFace-FFD21E?style=flat-square&logo=huggingface&logoColor=black)

**Backend & Infrastructure**
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazonaws&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)

**Observability & Analysis**
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat-square&logo=grafana&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat-square&logo=prometheus&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)

</details>

---

## 📈 Activity

<p align="center">
  <img src="./assets/activity.svg" width="98%" alt="Contribution activity" />
</p>

<p align="center">
  <img src="./assets/stats.svg" height="220" alt="GitHub stats" />
  <img src="./assets/streak.svg" height="220" alt="Contribution streak" />
</p>

<p align="center">
  <img src="./assets/langs.svg" height="180" alt="Most used languages" />
</p>

<p align="center"><sub>
  These cards are generated daily by <a href="./.github/workflows/stats.yml">a GitHub Action</a> in this repo
  using my own token — so unlike the shared public card services they include private contributions,
  and they can't go down when someone else's rate limit runs out.
</sub></p>

---

## 🏆 Education & Achievements

- 🎓 **IIT (BHU) Varanasi** — B.Tech, Mechanical Engineering · CPI 8.44
- 🥈 **Kshitij 2024, IIT Kharagpur** — Runner-up, Data Science Hackathon
- 📝 **GATE DA 2024** — AIR 3736
- 🤖 **Tech Lead**, RoboReg Robotics Club, IIT BHU

---

<p align="center">
  <a href="https://sagar-srivastava.com"><img src="https://img.shields.io/badge/Portfolio-000000?style=flat-square&logo=google-chrome&logoColor=white" /></a>
  <a href="https://linkedin.com/in/sagar-srivastavaa"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white" /></a>
  <a href="mailto:sagar.sriv.47@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white" /></a>
  <a href="https://instagram.com/still_sagar"><img src="https://img.shields.io/badge/Instagram-E4405F?style=flat-square&logo=instagram&logoColor=white" /></a>
</p>

<p align="center"><em>"If you can't measure it, you can't improve it."</em></p>
