import videoRulesData from "../../../shared/video-rules.json";

type PlatformRule = {
  id: string;
  displayName: string;
  aliases: string[];
  referer: string;
  useBrowserCookies: boolean;
};

type VideoRules = {
  shareTextUrlPattern: string;
  shareTextTrailingPunctuationPattern: string;
  platforms: PlatformRule[];
};

const videoRules = videoRulesData as VideoRules;

export const videoPlatforms = videoRules.platforms;

export function extractShareUrl(text: string): string {
  const match = text.match(new RegExp(videoRules.shareTextUrlPattern));
  if (!match) {
    return text.trim();
  }

  return match[0].replace(new RegExp(videoRules.shareTextTrailingPunctuationPattern), "");
}

export function getPlatformLabel(platformId: string): string {
  return videoPlatforms.find((platform) => platform.id === platformId)?.displayName ?? platformId;
}
