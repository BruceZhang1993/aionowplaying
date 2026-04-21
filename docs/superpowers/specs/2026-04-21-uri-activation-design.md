# aionowplaying URI 激活与 OpenUri 跨平台方案文档

**日期**: 2026-04-21
**作者**: Codex + Bruce
**状态**: 草案

## 背景

当前项目在 Linux 平台通过 MPRIS2 暴露 `OpenUri`，对应 D-Bus `org.mpris.MediaPlayer2.Player.OpenUri` 方法。

在 macOS 和 Windows 平台，项目已经分别接入：

- macOS: `MPNowPlayingInfoCenter` + `MPRemoteCommandCenter`
- Windows: `SystemMediaTransportControls`（SMTC）

issue #17 关注的问题，是在 macOS 和 Windows 上如何补齐与 `OpenUri` 语义接近的能力，以及宿主应用如何真正“接收 URI 并处理”。

## 问题定义

这里实际上存在两个容易混淆但必须拆开的能力：

### 1. 应用内打开 URI

指库或宿主应用在本地代码中收到一个 URI 字符串后，主动调用系统 API 打开它，例如：

- macOS: `NSWorkspace.open(_:)`
- Windows: `Launcher.LaunchUriAsync` 或 `ShellExecute`

这类能力的本质是“应用主动发起打开动作”。

### 2. 应用被外部 URI 激活

指系统或外部应用通过类似 `myplayer://...` 的协议唤起宿主应用，并把 URI 作为参数传入。

这类能力的本质是“应用成为 URI scheme handler，并在启动或激活时接收 URI”。

`OpenUri` 的跨平台实现如果只做到第 1 类能力，只能支持“本地调用打开 URI”；如果要支持“应用接受这个 URI”，就必须补上第 2 类能力。

## 官方能力边界

### macOS: MPNowPlaying / MPRemoteCommandCenter

Apple 官方文档中：

- `MPNowPlayingInfoCenter` 的职责是展示当前播放信息
- `MPRemoteCommandCenter` 的职责是接收系统媒体控制命令

它们支持的命令集中在：

- 播放 / 暂停 / 停止
- 上一首 / 下一首
- 播放位置变更
- 播放速率
- 循环 / 随机
- 评分、喜欢、不喜欢、书签等媒体交互

没有 `OpenUri`、`OpenURL` 或“让系统媒体中心把一个 URI 传给应用”的命令入口。

因此，macOS 上不能通过 `MPNowPlaying` 体系直接承载 `OpenUri`。

### Windows: SMTC

Microsoft 官方文档中，`SystemMediaTransportControls` 也是媒体控制入口，而不是 URI 激活入口。

它支持的能力集中在：

- 播放 / 暂停 / 停止
- 上一首 / 下一首
- 快进 / 快退
- 播放位置
- 速率、循环、随机
- 元数据与时间线展示

同样没有“OpenUri”类按钮、事件或激活路径。

因此，Windows 上也不能通过 SMTC 直接承载 `OpenUri`。

## 核心结论

macOS 的 `MPNowPlaying` 与 Windows 的 `SMTC` 都不能直接实现“系统媒体接口向应用下发 OpenUri”。

如果目标是跨平台补齐 `OpenUri` 能力，必须采用“双层设计”：

1. 媒体控制层继续使用各平台现有能力
2. URI 激活层由宿主应用单独实现

也就是说：

- `aionowplaying` 可以定义统一的 `OpenUri` 抽象
- 但真正接收 URI 的动作，不能依赖 `MPNowPlaying` 或 `SMTC`
- 它必须由宿主应用注册协议并接收系统激活事件

## 目标

本方案希望实现以下能力：

1. 在 macOS 和 Windows 上提供与 Linux `OpenUri` 语义尽量一致的抽象
2. 允许宿主应用主动打开 URI
3. 允许宿主应用被外部 URI scheme 激活
4. 为无法由库独立完成的宿主集成部分提供 macOS 与 Windows 的实现示例
5. 在 README 与 Sphinx 文档中引用单独的示例页面，降低接入门槛
6. 保持 `aionowplaying` 作为跨平台媒体抽象层，而不是直接演变成完整桌面应用框架

## 非目标

本次方案不包含以下范围：

- 不在 macOS 或 Windows 上模拟完整 MPRIS D-Bus 服务
- 不要求 `MPNowPlaying` 或 `SMTC` 原生支持 `OpenUri`
- 不在库内部直接承担应用打包、安装器、注册表写入或 `.app` bundle 生成
- 不定义完整的 URI 播放协议生态，只定义最小可用方案
- 不要求库直接替代宿主应用完成最终安装或系统注册

## 方案候选

### 方案 A: 只实现本地 `open_uri()`

做法：

- macOS 平台在 `MacOSInterface` 中调用 `NSWorkspace.open`
- Windows 平台在 `WindowsInterface` 中调用系统 URI 打开 API
- 不提供“外部 URI 激活应用”的设计

优点：

- 实现最简单
- 对现有代码改动最小
- 可以快速关闭 issue #17 中“本地打开 URI”的部分诉求

缺点：

- 无法让应用真正接收外部 URI
- 无法支持宿主自定义 scheme 深链
- 与“应用接受这个 URI”的目标不一致

适用场景：

- 只需要在应用内部把 URI 交给系统默认处理器

### 方案 B: 库层定义统一抽象，宿主应用负责 URI 激活

做法：

- `aionowplaying` 保留统一的 `on_open_uri(uri)` 抽象
- 宿主应用负责注册自己的 URI scheme
- 宿主应用在被系统激活时解析 URI
- 宿主应用将目标 URI 再交给自己的播放逻辑或库层回调

优点：

- 角色边界清晰
- 与当前项目“库而非应用”的定位一致
- macOS 和 Windows 都有成熟官方机制支撑
- 可以同时支持“本地打开 URI”和“外部唤起应用”

缺点：

- 宿主应用需要额外实现协议注册和激活处理
- 库侧只能定义契约，不能单独完成端到端体验

适用场景：

- 当前仓库继续保持为跨平台媒体控制库

### 方案 C: 在库外提供一个官方宿主适配器或示例应用

做法：

- 在方案 B 的基础上
- 额外提供示例宿主工程，演示 macOS `.app` 和 Windows 桌面应用如何接收 URI

优点：

- 文档和示例更完整
- 降低宿主接入门槛

缺点：

- 会明显扩大当前仓库维护范围
- 需要处理平台打包、签名、分发等额外问题

适用场景：

- 后续希望把项目推广成“库 + 参考宿主”的组合方案

## 推荐方案

采用方案 B。

原因：

- 它最符合 `aionowplaying` 当前定位
- 它把“媒体控制能力”和“应用激活能力”清晰拆分
- 它既能覆盖 issue #17，也能为后续深链、第三方唤起、播放器接管协议留出空间
- 它不要求伪造 `MPNowPlaying`/`SMTC` 不具备的系统能力

## 推荐架构

### 分层模型

建议将跨平台能力明确分成三层：

1. 系统媒体层
   - Linux: MPRIS2
   - macOS: `MPNowPlayingInfoCenter` / `MPRemoteCommandCenter`
   - Windows: `SMTC`

2. URI 打开层
   - 提供“当前进程主动打开 URI”的能力
   - macOS 使用 `NSWorkspace`
   - Windows 使用官方 URI 启动 API

3. URI 激活层
   - 由宿主应用注册并接收自定义 scheme
   - 接收到 URI 后交给业务逻辑解析

### 责任边界

`aionowplaying` 负责：

- 定义统一抽象接口
- 为平台接口提供本地 `open_uri` 能力
- 允许宿主把“收到的 URI”注入到播放器逻辑中
- 提供宿主接入示例文档与参考代码片段

宿主应用负责：

- 注册 URI scheme
- 接收系统激活事件
- 解析 URI
- 决定是交给系统默认应用打开，还是在应用内加载播放

## 文档与示例交付要求

对于无法由库独立完成的能力，本方案要求同时提供“说明文档 + 平台示例”。

### 交付内容

至少增加两类单独页面：

1. macOS 宿主接入示例页
2. Windows 宿主接入示例页

每个页面都应独立成文，而不是只在 README 中放零散片段。

### 页面内容要求

每个示例页至少应包含：

- 该平台上为什么这部分能力不能由库单独完成
- 宿主应用需要负责哪些事情
- 最小可运行示例或接近可运行的参考代码
- URI 注册位置与接收入口说明
- 收到 URI 后如何转交给播放器逻辑
- 与 `aionowplaying` 的接口衔接方式

### README 引用要求

README 和 `README.zh-CN.md` 需要新增单独章节，明确说明：

- `on_open_uri` 在 macOS / Windows 上的限制
- “本地打开 URI”和“接收 URI 激活”是两件事
- 宿主接入示例文档的入口链接

README 不应承载全部平台细节，而应承担总览与跳转职责。

### Sphinx 文档引用要求

Sphinx 文档中需要把这些示例页纳入目录树，并至少从以下位置可达：

- `docs/index.rst`
- Quick Start 或单独的集成说明入口页

目标是让 Read the Docs 用户可以从文档首页进入这些平台示例，而不是只能从仓库根 README 查找。

## 平台设计

### macOS

#### 本地打开 URI

宿主或接口层可调用：

- `NSWorkspace.sharedWorkspace().openURL_(url)`

这适合“主动打开 URI”。

#### 接收 URI 激活

宿主应用需要：

- 以 `.app` bundle 形式运行
- 在 `Info.plist` 中注册 `CFBundleURLTypes`
- 在 AppKit 生命周期中接收外部 URL 激活事件

收到 URI 后，宿主应用应将其转换为内部统一格式，例如：

- 直接播放资源 URI
- 或解析宿主自定义协议，例如 `myplayer://open?target=...`

然后再进入自身播放逻辑。

#### 对本项目的含义

如果当前项目仅作为 Python 库存在，而没有自己的 `.app` 宿主，则“接收 URI 激活”无法由库单独完成。

因此需要额外提供一个 macOS 宿主接入示例页面，说明：

- `Info.plist` 中如何注册 URL scheme
- AppKit 生命周期中如何接收 URL
- 如何把收到的 URI 传回播放器逻辑

### Windows

#### 本地打开 URI

宿主或接口层可调用：

- 首选：`Windows.System.Launcher.LaunchUriAsync`
- 桌面应用兼容方案：`ShellExecute`

这适合“主动打开 URI”。

#### 接收 URI 激活

宿主应用需要：

- 注册自定义协议
- 打包应用可在 manifest 中声明协议
- 未打包桌面应用通常通过安装阶段写入注册表实现协议关联

当用户或外部程序打开该协议时：

- 系统拉起宿主应用
- 宿主应用从激活参数或命令行参数中拿到 URI
- 再进入自身逻辑处理

#### 对本项目的含义

与 macOS 相同，库本身不能替代宿主完成协议注册，只能提供统一接口和调用契约。

因此需要额外提供一个 Windows 宿主接入示例页面，说明：

- 打包应用如何声明协议，或未打包桌面应用如何完成协议关联
- 宿主应用如何获取激活参数或命令行参数
- 如何把收到的 URI 传回播放器逻辑

## 统一 URI 契约建议

建议定义一个最小统一参数契约，而不是强制规定统一的外部 scheme。

### 对外协议建议

协议 scheme 不由 `aionowplaying` 强制规定，应由宿主应用自行决定。

例如宿主可以采用：

```text
myplayer://open?target=<encoded-uri>
```

或者：

```text
examplemusic://play?target=<encoded-uri>
```

`aionowplaying` 只建议约定 URI 的参数结构和解析后如何交给播放器逻辑，不规定最终对外暴露的协议名。

优点：

- 不绑死宿主品牌或产品命名
- 更符合库定位，而不是应用框架定位
- 仍然可以约定统一的参数结构，例如 `target`、`playlist`、`position`、`source`

### 宿主内部处理建议

宿主接收到 URI 后分两步：

1. 解析 scheme 和 action
2. 提取 `target`

随后根据业务需要二选一：

- 交给系统默认应用处理
- 在播放器内部自行加载

## 对代码结构的建议

### 库层最小能力

建议保持现有 `BaseInterface.on_open_uri(uri)` 作为统一抽象入口。

同时可考虑新增一个更明确的宿主协作层抽象，例如：

- `handle_activated_uri(uri: str)`

用途是区分：

- `on_open_uri`：系统媒体层希望应用打开某个 URI
- `handle_activated_uri`：宿主应用被外部协议唤起后，把 URI 交回应用逻辑

这两个入口最终可以复用相同业务逻辑，但语义上建议区分，以免后续概念混乱。

### 宿主接入契约

建议在文档中明确宿主最少要实现：

1. 注册协议
2. 接收系统传入的 URI
3. 调用统一解析函数
4. 将解析结果交给播放器控制层

## 测试策略建议

由于 URI 激活涉及真实系统环境，CI 不应依赖桌面环境做端到端验证。

建议测试拆成三层：

### 1. 纯解析测试

测试统一 URI 格式解析，例如：

- 合法 scheme
- 缺失 `target`
- 非法 action
- 编码后 URI 还原

### 2. 平台 opener 测试

通过 mock 验证：

- macOS opener 正确调用 `NSWorkspace`
- Windows opener 正确调用 `LaunchUriAsync` 或 `ShellExecute`

### 3. 宿主适配示例测试

如果后续提供示例宿主，则只测试：

- 激活参数到内部处理函数的转发

不在 CI 中要求真实注册协议并唤起桌面应用。

### 4. 文档链接可达性检查

需要增加基础文档检查，确保：

- README 中引用的示例页面路径存在
- Sphinx `toctree` 正确包含示例页
- 本地构建文档时页面可访问

## 风险与限制

### 1. 库不能单独完成 URI 激活

没有宿主应用时，库无法直接成为系统协议处理器。

### 2. 平台注册流程不属于媒体接口本身

这部分是应用分发和系统集成问题，不应强行塞进 `MPNowPlaying` 或 `SMTC` 抽象层。

### 3. URI 安全性需要由宿主控制

宿主需要决定：

- 允许哪些 scheme
- 是否允许远程内容
- 是否限制本地文件访问

这些策略不建议由底层媒体接口层默认决定。

## 分阶段落地建议

### 第一阶段

先实现“本地打开 URI”：

- macOS: `NSWorkspace`
- Windows: `LaunchUriAsync` 或 `ShellExecute`

目标是补齐 issue #17 的最小跨平台能力。

### 第二阶段

补充统一 URI 参数契约文档与解析工具。

目标是让宿主应用有统一接入契约。

### 第三阶段

提供宿主接入示例与文档入口：

- macOS URL scheme 示例
- Windows protocol handler 示例
- README / README.zh-CN 引用入口
- Sphinx 独立页面与目录树入口

目标是打通“外部唤起应用”的完整链路。

## 最终建议

对于当前仓库，最合理的方向不是尝试让 `MPNowPlaying` 或 `SMTC` 原生支持 `OpenUri`，因为官方能力边界并不支持这样设计。

更合理的设计是：

- 把 `OpenUri` 视为跨平台抽象能力
- 在 macOS / Windows 上用本地系统 API 实现“主动打开 URI”
- 把“接收 URI 激活”交给宿主应用去完成
- 通过统一协议和回调契约把宿主与库连接起来

这样既符合官方平台模型，也与 `aionowplaying` 当前作为跨平台库的定位保持一致。

## 参考资料

- Apple `MPNowPlayingInfoCenter`
- Apple `MPRemoteCommandCenter`
- Apple `NSWorkspace`
- Apple custom URL scheme / `CFBundleURLTypes`
- Microsoft `SystemMediaTransportControls`
- Microsoft `Launcher.LaunchUriAsync`
- Microsoft URI activation / protocol handler
