import { config, fields, collection, singleton } from "@keystatic/core";

declare const process: { env: { NODE_ENV?: string } };

export default config({
  storage:
    process.env.NODE_ENV === "production"
      ? {
          kind: "github",
          repo: {
            owner: "atlas-phil",
            name: "atlas-phil-web",
          },
        }
      : { kind: "local" },

  collections: {
    posts: collection({
      label: "ブログ記事",
      slugField: "title",
      path: "src/content/posts/*/",
      format: { contentField: "content" },
      schema: {
        title: fields.slug({ name: { label: "タイトル" } }),
        publishedDate: fields.date({
          label: "公開日",
          validation: { isRequired: true },
        }),
        category: fields.select({
          label: "カテゴリ",
          options: [
            { label: "団員ブログ", value: "member-blog" },
            { label: "本番レポート", value: "concert-report" },
            { label: "【団員にきいてみた】シリーズ", value: "interview" },
          ],
          defaultValue: "member-blog",
        }),
        eyecatch: fields.image({
          label: "アイキャッチ画像",
          directory: "public/images/posts",
          publicPath: "/images/posts",
        }),
        content: fields.markdoc({
          label: "本文",
          options: {
            image: {
              directory: "public/images/posts",
              publicPath: "/images/posts",
            },
          },
        }),
      },
    }),
  },

  singletons: {
    schedule: singleton({
      label: "練習日程",
      path: "src/content/singletons/schedule",
      format: { contentField: "content" },
      schema: {
        content: fields.markdoc({ label: "練習日程の内容" }),
      },
    }),

    concert: singleton({
      label: "演奏会情報",
      path: "src/content/singletons/concert",
      format: { contentField: "content" },
      schema: {
        content: fields.markdoc({
          label: "演奏会情報の内容",
          options: {
            image: {
              directory: "public/images/concert",
              publicPath: "/images/concert",
            },
          },
        }),
      },
    }),

    recruitment: singleton({
      label: "団員募集",
      path: "src/content/singletons/recruitment",
      format: { contentField: "content" },
      schema: {
        isRecruiting: fields.checkbox({
          label: "現在募集中",
          defaultValue: true,
        }),
        content: fields.markdoc({ label: "募集内容" }),
      },
    }),

    updates: singleton({
      label: "新着・更新情報",
      path: "src/content/singletons/updates",
      schema: {
        items: fields.array(
          fields.object({
            date: fields.date({ label: "日付" }),
            text: fields.text({ label: "内容" }),
            url: fields.text({
              label: "リンクURL（任意）",
              validation: { isRequired: false },
            }),
          }),
          {
            label: "更新情報",
            itemLabel: (props) => props.fields.text.value ?? "新しい更新情報",
          },
        ),
      },
    }),
  },
});
