import click
import os
import subprocess
import asyncio
from pathlib import Path
from citekit import CiteKitClient

# CiteKit acts as our temporal orchestrator
client = CiteKitClient()

@click.group()
def cli():
    """Video Orchestrator: Semantic Timeline Navigation
    
    This tool enables concept-based navigation of video libraries,
    going beyond keyword search to extract logical temporal segments.
    """
    pass

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def index(directory):
    """Orchestrate: Generate structural maps for a video library.
    
    This command processes all videos in the specified directory and
    creates semantic maps showing chapters, topics, and timestamps.
    
    Example:
        python orchestrate_video.py index ./lectures
    """
    video_extensions = ('.mp4', '.mov', '.mkv', '.avi', '.webm')
    directory_path = Path(directory)
    files = [f for f in directory_path.iterdir() if f.suffix.lower() in video_extensions]
    
    if not files:
        print(f"[WARNING] No video files found in {directory}")
        print(f"[INFO] Supported formats: {', '.join(video_extensions)}")
        return

    async def _process():
        for f in files:
            print(f"[INFO] Mapping Structural DNA: {f.name}")
            try:
                resource_map = await client.ingest(str(f), "video")
                print(f"[SUCCESS] Mapped {len(resource_map.nodes)} semantic nodes")
            except Exception as e:
                print(f"[ERROR] Failed to map {f.name}: {str(e)}")

    asyncio.run(_process())
    print(f"\n[COMPLETE] Indexed {len(files)} videos")

@cli.command()
@click.argument('concept')
@click.option('--player', default='mpv', help='Video player to use (default: mpv)')
def seek(concept, player):
    """Seek: Find a concept and play the high-fidelity clip.
    
    Searches through all indexed videos for the specified concept
    and extracts + plays the relevant temporal segment.
    
    Example:
        python orchestrate_video.py seek "gradient descent"
        python orchestrate_video.py seek "introduction" --player vlc
    """
    
    async def _search():
        # CiteKit provides the list of all semantic maps
        try:
            resource_ids = client.list_maps()
        except Exception as e:
            print(f"[ERROR] Failed to list maps: {str(e)}")
            print("[INFO] Have you indexed any videos yet? Try: index <directory>")
            return
        
        if not resource_ids:
            print("[WARNING] No videos indexed yet")
            print("[INFO] Run: python orchestrate_video.py index <directory>")
            return

        print(f"[INFO] Searching {len(resource_ids)} indexed videos for '{concept}'...")
        
        for rid in resource_ids:
            try:
                resource_map = client.get_map(rid)
                
                # Find nodes matching the concept
                # (In a real Agent, an LLM would choose the node based on summaries)
                for node in resource_map.nodes:
                    node_id_lower = node.id.lower()
                    summary_lower = (node.summary or "").lower()
                    title_lower = (node.title or "").lower()
                    concept_lower = concept.lower()
                    
                    if (concept_lower in node_id_lower or 
                        concept_lower in summary_lower or 
                        concept_lower in title_lower):
                        
                        print(f"\n[FOUND] Concept in {rid}")
                        print(f"  Node: {node.title or node.id}")
                        if node.summary:
                            print(f"  Summary: {node.summary[:100]}...")
                        
                        # Resolve to a physical high-fidelity clip
                        evidence = client.resolve(rid, node.id)
                        
                        print(f"[EXTRACTED] {evidence.output_path}")
                        
                        # Orchestrate the playback
                        print(f"[PLAYING] Opening in {player}...")
                        try:
                            subprocess.run([player, str(evidence.output_path)], check=True)
                        except FileNotFoundError:
                            print(f"[ERROR] Video player '{player}' not found")
                            print(f"[INFO] Install {player} or use --player option")
                            print(f"[INFO] Clip saved at: {evidence.output_path}")
                        except Exception as e:
                            print(f"[ERROR] Failed to play: {str(e)}")
                            print(f"[INFO] Clip saved at: {evidence.output_path}")
                        
                        return
            except Exception as e:
                print(f"[ERROR] Error processing {rid}: {str(e)}")
                continue

        print(f"\n[NOT FOUND] No matches for '{concept}'")
        print("[INFO] Try a different search term or index more videos")

    asyncio.run(_search())

@cli.command()
def list():
    """List all indexed videos and their structural maps.
    
    Shows available videos and their semantic structure,
    helping you understand what content is available.
    """
    try:
        resource_ids = client.list_maps()
    except Exception as e:
        print(f"[ERROR] Failed to list maps: {str(e)}")
        return
    
    if not resource_ids:
        print("[INFO] No videos indexed yet")
        print("[INFO] Run: python orchestrate_video.py index <directory>")
        return

    print(f"\n[LIBRARY] {len(resource_ids)} videos indexed:\n")
    
    for rid in resource_ids:
        try:
            resource_map = client.get_map(rid)
            print(f"📹 {rid}")
            print(f"   Nodes: {len(resource_map.nodes)}")
            
            # Show first few nodes as preview
            preview_count = min(3, len(resource_map.nodes))
            for node in resource_map.nodes[:preview_count]:
                print(f"   • {node.title or node.id}")
            
            if len(resource_map.nodes) > preview_count:
                print(f"   ... and {len(resource_map.nodes) - preview_count} more\n")
            else:
                print()
        except Exception as e:
            print(f"   [ERROR] Could not load map: {str(e)}\n")

if __name__ == '__main__':
    cli()
