"""
ARIS Content Automation - Interactive Review & Approval Gate
Allows Aris to inspect generated clips and Gemini metadata, and approve or reject before publishing.
"""

import os
import sys
import json
import youtube_meta_publisher

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PENDING_FILE = os.path.join(PROJECT_DIR, "data", "logs", "pending_approvals.json")

def review_cli():
    if not os.path.exists(PENDING_FILE):
        print("No pending clips awaiting review.")
        return

    with open(PENDING_FILE, "r", encoding="utf-8") as f:
        try:
            pending = json.load(f)
        except Exception:
            pending = []

    if not pending:
        print("No pending clips awaiting review.")
        return

    print("=======================================================")
    print(f"  Pending Approvals Queue ({len(pending)} clips)")
    print("=======================================================\n")

    remaining = []
    for idx, item in enumerate(pending, 1):
        print(f"[{idx}/{len(pending)}] Clip: {os.path.basename(item.get('source_clip', 'Unknown'))}")
        print(f"  Generated File : {item.get('processed_short')}")
        print(f"  Duration       : {item.get('duration')}s")
        print(f"  Title          : {item.get('title')}")
        print(f"  Description    :\n{item.get('description')}")
        print(f"  Quality Score  : {item.get('quality_score')}/10")
        print(f"  Content Hash   : {item.get('content_hash')[:12]}...")
        print("-------------------------------------------------------")

        choice = input("Approve and Publish to YouTube & Facebook? (y = Yes, n = Skip/Keep, d = Discard): ").strip().lower()

        if choice == "y":
            print("[*] Publishing clip...")
            res = youtube_meta_publisher.publish_content(
                video_path=item["processed_short"],
                content_hash=item["content_hash"],
                title=item["title"],
                description=item["description"],
                tags=item.get("tags", [])
            )
            if res.get("success"):
                print("[+] Successfully published and recorded to duplicate ledger!")
                try:
                    if os.path.exists(item.get("source_clip", "")):
                        os.remove(item["source_clip"])
                except Exception:
                    pass
            else:
                print(f"[-] Publishing failed: {res.get('error')}")
                remaining.append(item)
        elif choice == "d":
            print("[-] Discarded clip.")
        else:
            print("[*] Skipped for now.")
            remaining.append(item)
        print("\n")

    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(remaining, f, indent=2)

    print(f"Review session completed. {len(remaining)} clip(s) remaining in queue.")

if __name__ == "__main__":
    review_cli()
