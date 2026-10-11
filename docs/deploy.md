# Deploying the demo app

All data in the app is synthetic. The app reads a **demo bundle** (registry tables, engine
cache, summaries) and contains no science of its own.

## 1. Build the bundle (Claude Code / any machine with the data)
```bash
uv run bsm export demo-bundle --dataset v1 --experiment E1_headline --experiment E2_adoption
# -> ./bundle/ (about 13 MB) and ./bundle.tar.gz (about 11 MB)
```

## 2. Local run (also the offline fallback at the congress)
```bash
uv sync --all-groups
BSM_BUNDLE_PATH=bundle uv run streamlit run app/Home.py
```
No network is needed once `bundle/` exists. Pedigree trees render in the browser
(`st.graphviz_chart`), so the Graphviz `dot` binary is not required.

## 3. Public URL [HUMAN: accounts and tokens]
Pick whichever works first.

### Option A: Streamlit Community Cloud (bundle from a GitHub release asset)
1. Create the GitHub repo and push (see `plan/STATUS.md`, P10 steps).
2. Create a GitHub release `v0.1.0` and upload `bundle.tar.gz` as a release asset. Copy the
   asset's download URL (right click "bundle.tar.gz" > Copy link address).
3. Go to https://share.streamlit.io, sign in with GitHub, click **Create app**.
4. Repository: `<you>/breeding-smarter`, branch `main`, main file `app/Home.py`.
5. **Advanced settings** > Python 3.12; **Secrets / environment**: add
   `BSM_BUNDLE_URL = "<asset URL from step 2>"`.
6. Requirements: Community Cloud installs from `pyproject.toml` with `uv`. If it does not pick
   up the extras, add a file `requirements.txt` with the single line `.[app]` and redeploy.
7. Click **Deploy**. First start downloads and unpacks the bundle (about 30 s).
8. Copy the app URL into `README.md`, the About page link and the poster QR code
   (`conference/` build scripts read it from `conference/links.yaml`).

### Option B: Hugging Face Spaces (bundle from the Hugging Face dataset repo)
1. https://huggingface.co/new-space: SDK **Streamlit**, hardware CPU basic, public.
2. Push the repo to the Space (or connect GitHub), set app file `app/Home.py`.
3. Upload `bundle.tar.gz` to the dataset repo (P10 task 10.7) and set the Space secret
   `BSM_BUNDLE_URL` to its "resolve" URL
   (`https://huggingface.co/datasets/<user>/breeding-smarter-synthetic/resolve/main/bundle.tar.gz`).
4. Wait for the build; copy the Space URL as in step 8 above.

## 4. Fallbacks for the talk
1. Public URL. 2. Local app with the network off (step 2; test it on the presentation
laptop with Wi-Fi off). 3. Screen recording of the demo script ([HUMAN], see
`conference/demo_script.md`).
