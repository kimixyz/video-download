import { videoPlatforms } from "@/lib/videoRules";

const supportedPlatformNamesText = videoPlatforms.map((platform) => platform.displayName).join("、");
const supportedPlatformCount = videoPlatforms.length;

const FAQS = [
  {
    q: "支持哪些平台解析下载？",
    a: `支持 ${supportedPlatformNamesText}，共 ${supportedPlatformCount} 个主流平台。`,
  },
  {
    q: "视频下载的清晰度如何？",
    a: "默认提供所有可用清晰度列表，最高支持 1080P HD 甚至更高。B站、YouTube 等平台需已在 Chrome 浏览器中登录对应账号。",
  },
  {
    q: "可以去除视频水印吗？",
    a: "可以。抖音使用无水印 API 接口，TikTok 同样支持无水印下载。其他平台原视频本身无内嵌水印。",
  },
  {
    q: "小红书图文为什么无法下载？",
    a: "目前仅支持小红书视频内容，纯图文笔记暂不提供下载功能。",
  },
  {
    q: "YouTube / TikTok / Twitter 无法访问怎么办？",
    a: "YouTube、TikTok、Twitter 需要本机网络能访问对应网站，如需代理请自行配置系统代理后再使用。",
  },
  {
    q: "解析失败怎么办？",
    a: "请确认链接为有效的视频页面链接（非分享文字中的短文本）。部分平台需要登录权限，请确保已在 Chrome 中登录对应账号后重试。",
  },
  {
    q: "下载的视频在哪里？",
    a: "视频会下载到浏览器默认的下载目录中，文件名即视频标题。",
  },
];

export default function FAQ() {
  return (
    <section className="py-12 px-4 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-center text-white mb-8">常见问题</h2>
      <div className="space-y-3">
        {FAQS.map((item, i) => (
          <details
            key={i}
            className="rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm overflow-hidden"
          >
            <summary className="w-full flex items-center justify-between px-5 py-4 text-left text-white font-medium hover:bg-white/5 transition-colors cursor-pointer list-none">
              <span>{item.q}</span>
              <svg
                className="w-5 h-5 text-gray-400 shrink-0 transition-transform duration-200 open:rotate-180"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
              </svg>
            </summary>
            <div className="px-5 pb-4 text-gray-400 text-sm leading-relaxed">
              {item.a}
            </div>
          </details>
        ))}
      </div>
    </section>
  );
}
