import { PuppeteerLaunchOptions } from "puppeteer";
import Rule from "./rule";
import { parseBatdongsanComVnItem } from "./callbacks";
import { CsvPipeline, LogItemPipeline } from "./pipeline-processors";
import { PipelineItemProcessor } from "./base-classes";

class CrawlerSettings {
    static startUrls: string[] = [
        "https://batdongsan.com.vn/ban-can-ho-chung-cu-xa-duong-xa-prj-vinhomes-ocean-park-gia-lam/ban-cat-lo-2n1wc-60m2-tai-tang-trung-ban-cong-dong-nam-1-75-ty-pr38349090",
        "https://batdongsan.com.vn/nha-dat-ban?vrs=1",
        "https://batdongsan.com.vn/nha-dat-cho-thue?vrs=1"
    ];

    static rules: Rule[] = [
        new Rule({
            allow: "/p[0-9]+?vrs=1$",
            follow: true
        }),
        new Rule({
            allow: "-pr[0-9]+$",
            follow: false,
            pageHandler: parseBatdongsanComVnItem
        })
    ];

    static browserLaunchOptions: PuppeteerLaunchOptions = {
        headless: "new",
        // executablePath: "/usr/bin/google-chrome",
        args: ['--disable-features=site-per-process']
    };

    static randomSleepDurationDomain: [number, number] = [3, 6];

    static skipImageRequests: boolean = true;

    static progressHistoryDirectory: string = `${__dirname}/../history`
}

class PipelineSettings {
    static processors: PipelineItemProcessor[] = [
        new LogItemPipeline(),
        new CsvPipeline(),
    ];
}

export {CrawlerSettings, PipelineSettings};