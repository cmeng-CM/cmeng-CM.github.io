---
title: SpringBoot 启动 —— 源码解析
tags: springboot
categories: springboot
abbrlink: 609270ec
date: 2020-08-17 16:13:12
---

<font size=7>SpringBoot 启动 —— 源码解析</font>

## 一、概述
本文从main方法的SpringApplication.run(SpringbootTestLockApplication.class, args)开始追踪源码的实现，通过分析源码的调用情况分析整个springboot启动过程的原理和相关的设计理念。  
**SPringboot版本：2.4.4**


## 二、创建SpringApplication实例
### 2.1、启动类
程序入口是启动类的main方法。通过运行SpringApplication.run()来实际启动服务。

```Java
启动类main：
public static void main(String[] args) {
        ConfigurableApplicationContext run = SpringApplication.run(SpringbootTestLockApplication.class, args);
    }
```

### 2.2、SpringApplication实例
#### 2.2.1、启动步骤
通过源码可以看到，启动分为两步：1、实例化SpringApplication，2、再执行实例的run()方法.
```Java
//run方法两层调用
public static ConfigurableApplicationContext run(Class<?> primarySource, String... args) {
  return run(new Class<?>[] { primarySource }, args);
}

public static ConfigurableApplicationContext run(Class<?>[] primarySources, String[] args) {
  return new SpringApplication(primarySources).run(args);
}
```

#### 2.2.2、SpringApplication构造函数
SpringApplication的构造方法主要是为了初始化SpringApplication的一些基础属性，例如主启动类、web应用类型、启动载入器、初始化器列表、监听器列表等。
```Java
//构造函数两层调用
public SpringApplication(Class<?>... primarySources) {
  this(null, primarySources);
}

@SuppressWarnings({ "unchecked", "rawtypes" })
public SpringApplication(ResourceLoader resourceLoader, Class<?>... primarySources) {

  //根据调用逻辑可知resourceLoader为Null。
  this.resourceLoader = resourceLoader;
  Assert.notNull(primarySources, "PrimarySources must not be null");
  //将Class数组参数赋值到SpringApplication.primarySources属性
  this.primarySources = new LinkedHashSet<>(Arrays.asList(primarySources));

  //获取固定应用类型：WebApplicationType.SERVLET（The application should run as a servlet-based web application and should start an embedded servlet web server.）  
  this.webApplicationType = WebApplicationType.deduceFromClasspath();

  //获取spring.factories中Bootstrapper对应的实例
  this.bootstrappers = new ArrayList<>(getSpringFactoriesInstances(Bootstrapper.class));

  //设置 spring.factories中ApplicationContextInitializer对应的实例
  setInitializers((Collection) getSpringFactoriesInstances(ApplicationContextInitializer.class));

  //设置 spring.factories中ApplicationListener对应的实例
  setListeners((Collection) getSpringFactoriesInstances(ApplicationListener.class));
  //获取当前启动类class
  this.mainApplicationClass = deduceMainApplicationClass();
}
```

##### 1、getSpringFactoriesInstances
获取所以META-INF/spring.factories下的接口及其实现类的对应关系。即在初始化启动载入器、初始化器、监听器时，均是调用getSpringFactoriesInstances方法，通过传入不同的Class类型获取到不同的实例。
```Java
private <T> Collection<T> getSpringFactoriesInstances(Class<T> type) {
		return getSpringFactoriesInstances(type, new Class<?>[] {});
	}

private <T> Collection<T> getSpringFactoriesInstances(Class<T> type, Class<?>[] parameterTypes, Object... args) {
    //获取ClassLoader——sun.misc.Launcher$AppClassLoader
		ClassLoader classLoader = getClassLoader();

    //获取指定type的接口实现类列表
    Set<String> names = new LinkedHashSet<>(SpringFactoriesLoader.loadFactoryNames(type, classLoader));

    //初始化type对应的接口实现类
    List<T> instances = createSpringFactoriesInstances(type, parameterTypes, classLoader, args, names);
		AnnotationAwareOrderComparator.sort(instances);
		return instances;
	}
```
* getClassLoader：获取SpringApplication.resourceLoader，当resourceLoader为Null时获取当前线程的ClassLoader。由构造函数可知，此处获取的是当前线程的ClassLoader。

##### 2、loadFactoryNames()
通过解析getSpringFactoriesInstances可以看到，通过SpringFactoriesLoader.loadFactoryNames()方法获取指定名称的所有类名称列表。即通过扫描资源文件META-INF/spring.factories来获取相关的键值对匹配关系并进行代码化解析。

```Java
public static final String FACTORIES_RESOURCE_LOCATION = "META-INF/spring.factories";

public static List<String> loadFactoryNames(Class<?> factoryType, @Nullable ClassLoader classLoader) {
		ClassLoader classLoaderToUse = classLoader;
		if (classLoaderToUse == null) {
			classLoaderToUse = SpringFactoriesLoader.class.getClassLoader();
		}
		String factoryTypeName = factoryType.getName();
		return loadSpringFactories(classLoaderToUse).getOrDefault(factoryTypeName, Collections.emptyList());
	}

private static Map<String, List<String>> loadSpringFactories(ClassLoader classLoader) {
  //如果缓存存在，则获取缓存中的数据
  Map<String, List<String>> result = cache.get(classLoader);
	if (result != null) {
		return result;
	}

	result = new HashMap<>();
	try {
    //缓存不存在，则通过解析 FACTORIES_RESOURCE_LOCATION 资源文件，解析里面不同接口类型及对应的类名称。并将数据存储入缓存中。
		Enumeration<URL> urls = classLoader.getResources(FACTORIES_RESOURCE_LOCATION);
		while (urls.hasMoreElements()) {
			URL url = urls.nextElement();
			UrlResource resource = new UrlResource(url);
			Properties properties = PropertiesLoaderUtils.loadProperties(resource);
			for (Map.Entry<?, ?> entry : properties.entrySet()) {
				String factoryTypeName = ((String) entry.getKey()).trim();
				String[] factoryImplementationNames =
						StringUtils.commaDelimitedListToStringArray((String) entry.getValue());
				for (String factoryImplementationName : factoryImplementationNames) {
					result.computeIfAbsent(factoryTypeName, key -> new ArrayList<>())
							.add(factoryImplementationName.trim());
				}
			}
		}

		// Replace all lists with unmodifiable lists containing unique elements
		result.replaceAll((factoryType, implementations) -> implementations.stream().distinct()
				.collect(Collectors.collectingAndThen(Collectors.toList(), Collections::unmodifiableList)));
		cache.put(classLoader, result);
	}
	catch (IOException ex) {
		throw new IllegalArgumentException("Unable to load factories from location [" +
				FACTORIES_RESOURCE_LOCATION + "]", ex);
	}
	return result;
}
```

##### 3、setListeners()
初始化所有监听器，并将监听器数组赋值到SpringApplication.listeners属性中，纯净的springboot初始化的监听器分别如下：  
org.springframework.boot.ClearCachesApplicationListener
org.springframework.boot.builder.ParentContextCloserApplicationListener
org.springframework.boot.context.FileEncodingApplicationListener
org.springframework.boot.context.config.AnsiOutputApplicationListener
org.springframework.boot.context.config.DelegatingApplicationListener
org.springframework.boot.context.logging.LoggingApplicationListener
org.springframework.boot.env.EnvironmentPostProcessorApplicationListener
org.springframework.boot.liquibase.LiquibaseServiceLocatorApplicationListener
org.springframework.boot.autoconfigure.BackgroundPreinitializer
 
  

自此SpringApplication初始化完成。主要是初始化了一些基础属性和定义了服务类型。


## 三、运行SpringApplication.run()方法
创建成功后调用该实例的run方法：运行spring应用程序，创建并刷新一个APplicationContext对象。  
ApplicationContext：中央接口，为应用程序提供配置。在应用程序运行时这是只读的，但如果实现支持，则可以重新加载。  

```Java
/**
	 * Run the Spring application, creating and refreshing a new
	 * {@link ApplicationContext}.
	 * @param args the application arguments (usually passed from a Java main method)
	 * @return a running {@link ApplicationContext}
	 */
public ConfigurableApplicationContext run(String... args) {

  //创建秒表
  StopWatch stopWatch = new StopWatch();
  //秒表启动
  stopWatch.start();

  //创建启动上下文
  DefaultBootstrapContext bootstrapContext = createBootstrapContext();
	ConfigurableApplicationContext context = null;

  // 设置系统参数：java.awt.headless（在系统可能缺少显示设备、键盘或鼠标这些外设的情况下可以使用该模式，例如Linux服务器）
  configureHeadlessProperty();

  //初始化监听器列表
  SpringApplicationRunListeners listeners = getRunListeners(args);

  //启动监听器
  listeners.starting(bootstrapContext, this.mainApplicationClass);
	try {
    //创建程序参数对象，args：命令行执行时，命令行参数对象。
    ApplicationArguments applicationArguments = new DefaultApplicationArguments(args);

    //准备环境
    ConfigurableEnvironment environment = prepareEnvironment(listeners, bootstrapContext, applicationArguments);

    //设置忽略的bean信息
    configureIgnoreBeanInfo(environment);

    //打印banner，即启动时控制台的图案
    Banner printedBanner = printBanner(environment);

    //根据webApplicationType来创建容器/spring上下文对象  下面统一称呼为容器
    context = createApplicationContext();

    //设置应用程序启动指标对象，使应用程序上下文在启动期间能够记录一些指标
		context.setApplicationStartup(this.applicationStartup);

    //准备容器，容器的前置处理
		prepareContext(bootstrapContext, context, environment, listeners, applicationArguments, printedBanner);

    //刷新容器
    refreshContext(context);

    //刷新容器的后续处理
    afterRefresh(context, applicationArguments);

    //秒表停止
    stopWatch.stop();

    //输出记录，记录启动类class信息，时间信息
    if (this.logStartupInfo) {
      new StartupInfoLogger(this.mainApplicationClass).logStarted(getApplicationLog(), stopWatch);
    }

    // 发布监听应用上下文启动完成（发出启动结束事件）
    listeners.started(context);

    //运行runner
    callRunners(context, applicationArguments);
  }
  catch (Throwable ex) {
    handleRunFailure(context, ex, listeners);
    throw new IllegalStateException(ex);
  }

  try {
    //监听容器运行中
    listeners.running(context);
  }
  catch (Throwable ex) {
    handleRunFailure(context, ex, null);
    throw new IllegalStateException(ex);
  }
  return context;
}
```
下面就是对整个run方法进行逐行理解分析。

### 3.1、秒表

创建一个秒表并在正式运行逻辑之前启动。纳秒级精确度。
```Java
StopWatch stopWatch = new StopWatch();
stopWatch.start();
```

### 3.2、创建启动上下文——Bootstrap

Spring Cloud官方文档有一部分相关Bootstrap的描述：  
[Spring Cloud 官方文档](https://cloud.spring.io/spring-cloud-commons/multi/multi__spring_cloud_context_application_context_services.html)    

大致译文为：
Spring Cloud应用程序通过创建**bootstrap**上下文进行操作，该上下文是主应用程序的父上下文。它负责从外部源加载配置属性，并负责解密本地外部配置文件中的属性。这两个上下文共享一个**Environment**，这是任何Spring应用程序的外部属性的来源。默认情况下，引导程序属性（不是bootstrap.properties引导程序阶段加载的属性）具有较高的优先级，因此它们不能被本地配置覆盖。  

如果从SpringApplication或构建应用程序上下文SpringApplicationBuilder，那么Bootstrap上下文将作为父级添加到该上下文。  

```Java
private DefaultBootstrapContext createBootstrapContext() {
		DefaultBootstrapContext bootstrapContext = new DefaultBootstrapContext();
		this.bootstrappers.forEach((initializer) -> initializer.intitialize(bootstrapContext));
		return bootstrapContext;
	}
```
进入源码，可知创建启动上下文时，会进行初始化，主要对bootstrapContext内的实例进行注册。注册成功后返回bootstrapContext对象。  
**注**：通过loadFactoryNames()方法可知当不应用Cloud体系时，bootstrapContext为空list。  

### 3.3、获取SpringApplicationRunListeners实例——getRunListeners()  
```java
private SpringApplicationRunListeners getRunListeners(String[] args) {
  Class<?>[] types = new Class<?>[] { SpringApplication.class, String[].class };
  return new SpringApplicationRunListeners(logger,
      getSpringFactoriesInstances(SpringApplicationRunListener.class, types, this, args),
      this.applicationStartup);
}
```
1. 这段代码就比较熟悉了，还是getSpringFactoriesInstances()这个方法获取所有SpringApplicationRunListener接口的实现类的实例化对象。并初始SpringApplicationRunListeners对象。  

2. SpringApplicationRunListener：spring所有事件的触发都是通过该接口的唯一实现类EventPublishingRunListener来实现的，EventPublishingRunListener也是该接口的官方唯一实现类。
EventPublishingRunListener构造函数：
```java
public EventPublishingRunListener(SpringApplication application, String[] args) {
		this.application = application;
		this.args = args;
		this.initialMulticaster = new SimpleApplicationEventMulticaster();
		for (ApplicationListener<?> listener : application.getListeners()) {
			this.initialMulticaster.addApplicationListener(listener);
		}
	}
```
EventPublishingRunListener的属性共有三个：
  * application：当前运行的SpringApplication实例
  * args：启动命令行参数
  * initialMulticaster：事件广播器
根据构造函数可知，会将application关联的所有ApplicationListener实例关联到initialMulticaster中，以方便initialMulticaster将事件传递给所有的监听器。

3. 事件触发过程：
  * 当对应的时间处理方法被调用时，EventPublishingRunListener会将application和args封装到对应的SpringApplicationEvent子类实例中；
  * initialMulticaster会根据事件类型和触发源对事件进行分类，并与对应的ApplicationListener建立关联关系，之后将事件传递给对应的ApplicationListener；
  * ApplicationListener实例收到事件后，会根据时间类型不同，执行不同的处理逻辑。

至此可知，getRunListeners()方法是为了获取一个装有EventPublishingRunListener对象实例的数组对象-SpringApplicationRunListeners。用于后续事件触发通知功能。

### 3.4、启动监听器——listeners.starting()

初始化所有监听器后，进行启动。启动时传入启动上下文和启动类的class对象
```Java
void starting(ConfigurableBootstrapContext bootstrapContext, Class<?> mainApplicationClass) {
		doWithListeners("spring.boot.application.starting", (listener) -> listener.starting(bootstrapContext),
				(step) -> {
					if (mainApplicationClass != null) {
						step.tag("mainApplicationClass", mainApplicationClass.getName());
					}
				});
	}
```

启动监听器主要是starting()方案，此处调用则使用SpringApplicationRunListener接口的实现类EventPublishingRunListener对应的starting()方法进行监听器启动。  
此处实现类的创建的可参看 spring-boot 包的 spring.factories 文件：[官方spring.factories](https://github.com/spring-projects/spring-boot/blob/master/spring-boot-project/spring-boot/src/main/resources/META-INF/spring.factories)  

EventPublishingRunListener具体实现启动的代码逻辑
```Java
@Override
	public void starting(ConfigurableBootstrapContext bootstrapContext) {
		this.initialMulticaster
				.multicastEvent(new ApplicationStartingEvent(bootstrapContext, this.application, this.args));
}

@Override
public void multicastEvent(final ApplicationEvent event, @Nullable ResolvableType eventType) {
  ResolvableType type = (eventType != null ? eventType : resolveDefaultEventType(event));
  Executor executor = getTaskExecutor();
  for (ApplicationListener<?> listener : getApplicationListeners(event, type)) {
    if (executor != null) {
      executor.execute(() -> invokeListener(listener, event));
    }
    else {
      invokeListener(listener, event);
    }
  }
}

protected void invokeListener(ApplicationListener<?> listener, ApplicationEvent event) {
  ErrorHandler errorHandler = getErrorHandler();
  if (errorHandler != null) {
    try {
      doInvokeListener(listener, event);
    }
    catch (Throwable err) {
      errorHandler.handleError(err);
    }
  }
  else {
    doInvokeListener(listener, event);
  }
}

private void doInvokeListener(ApplicationListener listener, ApplicationEvent event) {
  try {
    listener.onApplicationEvent(event);
  }
  ......
}
```
starting()启动的时候实际上是又创建了一个ApplicationStartingEvent对象，其实就是监听应用启动事件。其中 initialMulticaster是一个SimpleApplicationEventMuticaster对象的实例化。
具体：
  * 获取initialMulticaster的线程池，但该实例初始化时并未创建线程池对象，所以此处为null
  * 通过getApplicationListeners方法获取匹配事件的监听器。
  * 对符合要求的监听器执行invokeListener方法.
  * 对符合条件的监听器执行onApplicationEvent方法进行相关初始化操作。

此处纯净的springboot项目共有四个监听器。
 * LoggingApplicationListener初始化了loggingSystem
 * BackgroundPreinitializer：未执行任何操作
 * DelegatingApplicationListener：未执行任何操作
 * LiquibaseServiceLocatorApplicationListener：未执行任何操作.


### 3.5、环境准备-prepareEnvironment()

设置好监听器后进行环境准备。主要是初始化应用参数和启动环境准备，源码对应如下：
```Java
//创建程序参数对象，args：命令行执行时，命令行参数对象。
ApplicationArguments applicationArguments = new DefaultApplicationArguments(args);

ConfigurableEnvironment environment = prepareEnvironment(listeners, bootstrapContext, applicationArguments);

//设置忽略的bean信息
configureIgnoreBeanInfo(environment);
```

#### 3.5.1、初始化应用参数

对启动时的参数进行解析，例如：java -jar --spring.profiles.active=test等。最终将解析的键值对存储到CommandLineArgs对象中。

#### 3.5.2、准备环境
```Java
	private ConfigurableEnvironment prepareEnvironment(SpringApplicationRunListeners listeners,
			DefaultBootstrapContext bootstrapContext, ApplicationArguments applicationArguments) {
		// 获取或创建一个environment实例
		ConfigurableEnvironment environment = getOrCreateEnvironment();

    //配置环境：转换器、命令行参数等
		configureEnvironment(environment, applicationArguments.getSourceArgs());

    //固定ConfigurationPropertySourcesPropertySource到environment
		ConfigurationPropertySources.attach(environment);

    //启动监听器
		listeners.environmentPrepared(bootstrapContext, environment);
    //判断是否存在defaultProperties的属性源，存在则移动最后一位
		DefaultPropertiesPropertySource.moveToEnd(environment);
    
		configureAdditionalProfiles(environment);

    //将环境绑定到SpringApplication类上
		bindToSpringApplication(environment);

    //判断是否存在定制的环境
		if (!this.isCustomEnvironment) {
			environment = new EnvironmentConverter(getClassLoader()).convertEnvironmentIfNecessary(environment,
					deduceEnvironmentClass());
		}
		ConfigurationPropertySources.attach(environment);
		return environment;
	}
```
##### 1、getOrCreateEnvironment()
```Java
private ConfigurableEnvironment getOrCreateEnvironment() {
		if (this.environment != null) {
			return this.environment;
		}
		switch (this.webApplicationType) {
		case SERVLET:
			return new StandardServletEnvironment();
		case REACTIVE:
			return new StandardReactiveWebEnvironment();
		default:
			return new StandardEnvironment();
		}
	}
```
如果不存在environment则根据webApplicationType类型进行初始环境实例创建，通过上面的源码解析可知，此处类型为SERVLET，所以会创建StandardServletEnvironment实例。  
StandardReactiveWebEnvironment构造：
* 调用了父类AbstractEnvironment的构造函数，进行相关属性的初始化。
  1. propertySources属性初始化MutablePropertySources实例。
  2. propertyResolver属性初始化PropertySourcesPropertyResolver实例，它的父类AbstractPropertyResolver中定义了"${}"占位符，用于后续解析配置文件时使用。
* 通过customizePropertySources()方法对propertySources增加了以下四个元素：servletConfigInitParams、servletContextInitParams、systemProperties、systemEnvironment。

##### 2、configureEnvironment(environment, applicationArguments.getSourceArgs());
```Java
protected void configureEnvironment(ConfigurableEnvironment environment, String[] args) {
  if (this.addConversionService) {
    ConversionService conversionService = ApplicationConversionService.getSharedInstance();
    environment.setConversionService((ConfigurableConversionService) conversionService);
  }
  configurePropertySources(environment, args);
  configureProfiles(environment, args);
}
```
环境配置分三步，配置转换器、配置属性资源(命令行参数)、配置文件(命令行参数)。
* 配置转换器：
  1. addConversionService属性初始值为true，通过静态方法getSharedInstance()获取一个单例的转换器。构造函数包含一些默认的Formatter和GenericConverter。
  2. 获取后配置到environment的propertyResolver属性中。
* 配置属性资源文件:configurePropertySources()
  ```Java
  private boolean addCommandLineProperties = true;
  public static final String COMMAND_LINE_PROPERTY_SOURCE_NAME = "commandLineArgs";

  protected void configurePropertySources(ConfigurableEnvironment environment, String[] args) {
		MutablePropertySources sources = environment.getPropertySources();
		if (!CollectionUtils.isEmpty(this.defaultProperties)) {
			DefaultPropertiesPropertySource.addOrMerge(this.defaultProperties, sources);
		}
    //若条件成立则将命令行参数设置进环境属性资源
		if (this.addCommandLineProperties && args.length > 0) {
			String name = CommandLinePropertySource.COMMAND_LINE_PROPERTY_SOURCE_NAME;
			if (sources.contains(name)) {
				PropertySource<?> source = sources.get(name);
				CompositePropertySource composite = new CompositePropertySource(name);
				composite.addPropertySource(
						new SimpleCommandLinePropertySource("springApplicationCommandLineArgs", args));
				composite.addPropertySource(source);
				sources.replace(name, composite);
			}
			else {
				sources.addFirst(new SimpleCommandLinePropertySource(args));
			}
		}
	}
  ```
  初始化defaultProperties属性为null，args则根据是否在命令输入进行相关处理。
* 配置文件(命令行参数):configureProfiles()
  ```Java
  protected void configureProfiles(ConfigurableEnvironment environment, String[] args) {
	}
  ```
  未具体实现，应该是用于后续扩展使用。

##### 3、ConfigurationPropertySources.attach(environment)
```Java
private static final String ATTACHED_PROPERTY_SOURCE_NAME = "configurationProperties";

public static void attach(Environment environment) {
  Assert.isInstanceOf(ConfigurableEnvironment.class, environment);
  MutablePropertySources sources = ((ConfigurableEnvironment) environment).getPropertySources();
  PropertySource<?> attached = sources.get(ATTACHED_PROPERTY_SOURCE_NAME);
  if (attached != null && attached.getSource() != sources) {
    sources.remove(ATTACHED_PROPERTY_SOURCE_NAME);
    attached = null;
  }
  if (attached == null) {
    sources.addFirst(new ConfigurationPropertySourcesPropertySource(ATTACHED_PROPERTY_SOURCE_NAME,
        new SpringConfigurationPropertySources(sources)));
  }
}
```
该步骤的目的是将ConfigurationPropertySource支持固定到environment中，以便于PropertySourcesPropertyResolver使用配置属性名称进行解析。

##### 4、listeners.environmentPrepared(bootstrapContext, environment)
```Java
void environmentPrepared(ConfigurableBootstrapContext bootstrapContext, ConfigurableEnvironment environment) {
		doWithListeners("spring.boot.application.environment-prepared",
				(listener) -> listener.environmentPrepared(bootstrapContext, environment));
	}
```
向监听器发送环境准备事件。此处的代码就比较熟悉了，和启动监听事件[starting()]方法逻辑基本一致。此处主要用来解析配置文件的监听器为：EnvironmentPostProcessorApplicationListener。
![springboot配置读取调用层次关系](/image/springboot/springboot-yml读取过程.png)  

##### 5、DefaultPropertiesPropertySource.moveToEnd(environment)
判断是否存在defaultProperties的属性源，存在则移动最后一位

##### 6、configureAdditionalProfiles(environment);
```Java
private void configureAdditionalProfiles(ConfigurableEnvironment environment) {
		if (!CollectionUtils.isEmpty(this.additionalProfiles)) {
			Set<String> profiles = new LinkedHashSet<>(Arrays.asList(environment.getActiveProfiles()));
			if (!profiles.containsAll(this.additionalProfiles)) {
				profiles.addAll(this.additionalProfiles);
				environment.setActiveProfiles(StringUtils.toStringArray(profiles));
			}
		}
	}
```
此处获取additionalProfiles属性是通过SpringApplicationBuilder实例设置的，一般不是使用SpringApplicationBuilder对象的应用此处没有额外的配置进入。

##### 7、bindToSpringApplication(environment)
将环境绑定到SpringApplication类上

##### 8、if (!this.isCustomEnvironment)
判断是否存在定制的环境，一般springboot方式启动的服务该**isCustomEnvironment**均为false，只有当通过SpringApplicationBuilder以war包的形式启动才会对该参数进行true赋值。

##### 9、ConfigurationPropertySources.attach(environment)
通过lister的一系列操作后再次将ConfigurationPropertySource支持固定到environment中。

自此Springboot启动流程中环境准备、配置等操作已完成。
	

#### 3.6、准备容器，容器的前置处理——prepareContext(bootstrapContext, context, environment, listeners, applicationArguments, printedBanner);
参数属性对应的实际class类型：
  * contex:AnnotationConfigServletWebServerApplicationContext
  * listeners: SpringApplicationRunListeners

```java
	private void prepareContext(DefaultBootstrapContext bootstrapContext, ConfigurableApplicationContext context,
			ConfigurableEnvironment environment, SpringApplicationRunListeners listeners,
			ApplicationArguments applicationArguments, Banner printedBanner) {
		
    //将给定的环境委托给底层的AnnotatedBeanDefinitionReader和ClassPathBeanDefinitionScanner。
    context.setEnvironment(environment);
		postProcessApplicationContext(context);
		applyInitializers(context);
		listeners.contextPrepared(context);
		bootstrapContext.close(context);
		if (this.logStartupInfo) {
			logStartupInfo(context.getParent() == null);
			logStartupProfileInfo(context);
		}
		// Add boot specific singleton beans
		ConfigurableListableBeanFactory beanFactory = context.getBeanFactory();
		beanFactory.registerSingleton("springApplicationArguments", applicationArguments);
		if (printedBanner != null) {
			beanFactory.registerSingleton("springBootBanner", printedBanner);
		}
		if (beanFactory instanceof DefaultListableBeanFactory) {
			((DefaultListableBeanFactory) beanFactory)
					.setAllowBeanDefinitionOverriding(this.allowBeanDefinitionOverriding);
		}
		if (this.lazyInitialization) {
			context.addBeanFactoryPostProcessor(new LazyInitializationBeanFactoryPostProcessor());
		}
		// Load the sources
		Set<Object> sources = getAllSources();
		Assert.notEmpty(sources, "Sources must not be empty");
		load(context, sources.toArray(new Object[0]));
		listeners.contextLoaded(context);
	}
```










未完待续！
















