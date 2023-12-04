# Changelog

## [0.3.1](https://github.com/engisalor/quartz/compare/v0.3.0...v0.3.1) (2023-12-04)


### Bug Fixes

* add crossfilter to query page, fixes ([275d7e8](https://github.com/engisalor/quartz/commit/275d7e87a5bef22f9ab7edc8bf3e65b14af5b72c))
* add error handling to query ([b98d0e2](https://github.com/engisalor/quartz/commit/b98d0e2a436b571c5732797bc385105d723cbf09))
* add local gitignore dir ([ac8f7c5](https://github.com/engisalor/quartz/commit/ac8f7c50dbfc952d37c048eba3330611497c5ee0))
* add url module ([fddf83c](https://github.com/engisalor/quartz/commit/fddf83c345d9e77891a4ec88bb771152a8cdb7cc))
* allow  no debug var, add corpus colors ([5f1c461](https://github.com/engisalor/quartz/commit/5f1c461fcef6f96f95952c92b34fe53926f86862))
* choropleth frq annotation ([c42678d](https://github.com/engisalor/quartz/commit/c42678d5258325812e11e76315d6b78798166cc5))
* corpora page add default header ([3b32d95](https://github.com/engisalor/quartz/commit/3b32d95e1c9a10eefeee4e87a884be70c705d9c7))
* css responsiveness, new components ([a136f00](https://github.com/engisalor/quartz/commit/a136f003ad737ec39de9a066190c61fcded2d1d7))
* fix md file loading error ([694cc3c](https://github.com/engisalor/quartz/commit/694cc3c249b715a438978b078607430b96be937d))
* freqs data_table fix err if no data ([6804c6d](https://github.com/engisalor/quartz/commit/6804c6de9c040e7d2328549c64d7baf5a6ae2fac))
* improve aio component for graph group ([eaa1340](https://github.com/engisalor/quartz/commit/eaa1340ac1ec3906afac3ac6a860a57bf8330542))
* improve query page warnings ([5c8c39f](https://github.com/engisalor/quartz/commit/5c8c39f3242085235c67950247ea2361d1ee6955))
* release-please files ([e95fb25](https://github.com/engisalor/quartz/commit/e95fb2585876b4eb7fc67f508a841df20922ca17))
* remove params from csv download ([be29437](https://github.com/engisalor/quartz/commit/be29437b2edfe2390e1ad17079aae85d4a2a331b))
* split freqs_viz file, various fixes ([679ed24](https://github.com/engisalor/quartz/commit/679ed24bf7d3d8e2c796eaaa526a289f3f92a430))
* update example config yaml files ([f1ea60e](https://github.com/engisalor/quartz/commit/f1ea60ea87562aa4505d9068cc23eaffe761742a))
* use `alc,` for query strings ([b7cb807](https://github.com/engisalor/quartz/commit/b7cb807c5a1b7d6c9835fa0a0d7b498a4c8357e6))


### Documentation

* add color code to config examples ([c2af5e3](https://github.com/engisalor/quartz/commit/c2af5e3a760f8cf5a555908409b5d03c872f3330))
* add license notice ([5827993](https://github.com/engisalor/quartz/commit/5827993db810da1464a48a3f91d9ad0904207368))
* update env-example ([5db2e40](https://github.com/engisalor/quartz/commit/5db2e40cfa77fa8b09e66eedc8147bcec83758ae))
* update guide ([224dec3](https://github.com/engisalor/quartz/commit/224dec3c6712b288be962e89f63a8e34e5966d97))
* update readme ([9ce74be](https://github.com/engisalor/quartz/commit/9ce74be6d10a09d1158b3403d9306da743dd0669))
* update user guide ([b08ae80](https://github.com/engisalor/quartz/commit/b08ae80748e75319c53befdff3d4a164cea61c19))

## [0.3.0](https://github.com/engisalor/quartz/compare/v0.2.1...v0.3.0) (2023-10-19)


### ⚠ BREAKING CHANGES

* redo settings attrs, funcs

### Bug Fixes

* add choropleth viz, refactor vizzes ([a73f43c](https://github.com/engisalor/quartz/commit/a73f43c13b20ada5560ba6ca267dbd356a4d886e))
* add config volume to compose file ([cb5b0d8](https://github.com/engisalor/quartz/commit/cb5b0d863e3b61e8a90557fee8581795b13822f5))
* add corpora-ske.yml example ([49ef511](https://github.com/engisalor/quartz/commit/49ef51148e401d8e7598593d357bcc6b99d63379))
* add labels to dockerfile ([5e56614](https://github.com/engisalor/quartz/commit/5e566147e71185a950df06bae16936f880047e77))
* add params to stored data ([336af00](https://github.com/engisalor/quartz/commit/336af003bcb0013208ef9516a941bc1380ed9791))
* add ske_graph AIO module ([98a1461](https://github.com/engisalor/quartz/commit/98a14612d2f1596cd4b7b054f9cb28881573416f))
* deprecate redirect policy ([65aa297](https://github.com/engisalor/quartz/commit/65aa2971eda72143302d56e439e5c3632fa7ef95))
* guide-button placement ([79f6331](https://github.com/engisalor/quartz/commit/79f6331a0c2e13d6a62c1e28bb96cf31b2beb851))
* markdown aio allow None, default to "" ([bcbe007](https://github.com/engisalor/quartz/commit/bcbe0073ee2b976932716121b083ce994d07b335))
* move markdown/ to config/ ([71a4495](https://github.com/engisalor/quartz/commit/71a44958586c4c9654c536cc0e9cdff5c5d19e8a))
* move settings to base dir (del environment) ([57417d7](https://github.com/engisalor/quartz/commit/57417d720c91154217655f143163ac58b4ab2232))
* redo env variable parsing ([034ca4d](https://github.com/engisalor/quartz/commit/034ca4db600d7d6f532872060e6b3307e06fde42))
* redo settings attrs, funcs ([590ba68](https://github.com/engisalor/quartz/commit/590ba68ba5be01451b28f8988a5c6b873b174995))
* remove builtin .env examples ([e85ff08](https://github.com/engisalor/quartz/commit/e85ff0827a0ff25c7e50ffafd3ba6bfe2f972c48))
* remove redirect, home_md env attrs, add guide ([2c736b0](https://github.com/engisalor/quartz/commit/2c736b03a0277c84fb92cfbf06846bfcf73a3d82))
* rename pages files, rm home, update copy_url ([110fe2f](https://github.com/engisalor/quartz/commit/110fe2fbec7e69767fbca58d05cf97dd3ec658dc))
* update app.py ([944f05a](https://github.com/engisalor/quartz/commit/944f05a372cfa5a14b4719cf0efd8ff1849eecf3))
* update corpora aio ([68aa585](https://github.com/engisalor/quartz/commit/68aa58508add9e61caabc9930157ac1b1f59cbc1))
* update corpora page ([bfe03cc](https://github.com/engisalor/quartz/commit/bfe03cc9091b391650c0ec23dd0a0fc7b4d8d489))
* update docker files ([611e6c4](https://github.com/engisalor/quartz/commit/611e6c494bce6f103e44676648492cc2c069173d))
* update dockerfile ([3b5c323](https://github.com/engisalor/quartz/commit/3b5c32321233eeaefbaaa2a9941614bfe82a56f1))
* update env example ([364081a](https://github.com/engisalor/quartz/commit/364081a840f8210c17ec30aa6f9597bc0581fef9))
* update env, ignore files ([aa90ee0](https://github.com/engisalor/quartz/commit/aa90ee0ac2f602e2bf7f4e4da73d4da7714eb555))
* update freqs_viz, settings,  for url gener. ([550a2a2](https://github.com/engisalor/quartz/commit/550a2a206fc459000aa9ad8d036e8bc4feab286a))
* update frequencies page ([1919c39](https://github.com/engisalor/quartz/commit/1919c391e90133847e413a5ee9a0278995cf295d))
* update frequencies visualization funcs ([6dbf2f3](https://github.com/engisalor/quartz/commit/6dbf2f33c1ba1e5afa7ace17c35d044af55076c6))
* update ignore and env files ([9239a11](https://github.com/engisalor/quartz/commit/9239a111411fb3f66c3706d9915795d5d2dc8841))
* update ignore files ([f7699c0](https://github.com/engisalor/quartz/commit/f7699c03b77923df59186160eb2bf54ec6cd5210))
* update import paths for settings ([f427fe5](https://github.com/engisalor/quartz/commit/f427fe5a4e182037834556ca7b0e685d2b4c4def))
* update layout sidebar ([529b219](https://github.com/engisalor/quartz/commit/529b219888a861cbc61304661a2cbf3ce03623ed))
* update redirect ([35cc132](https://github.com/engisalor/quartz/commit/35cc1325b30ec8e633e402dc97244e3be26fdf50))
* update sidebar icon ([3e02890](https://github.com/engisalor/quartz/commit/3e028900ecf8d174f80ab4eab5bb898ffa7243d3))


### Documentation

* add interpretation note to guide ([1fcd7ff](https://github.com/engisalor/quartz/commit/1fcd7ff7a8e8afc509dcfc797d636c70f1bd5ae3))
* update guide, env example ([d148632](https://github.com/engisalor/quartz/commit/d14863232343c64736f19a42fb487b8ef031b934))
* update readme, citation ([e12d7d5](https://github.com/engisalor/quartz/commit/e12d7d51ccfc5743716cc29454b49a099eabb04e))

## [0.2.1](https://github.com/engisalor/quartz/compare/v0.2.0...v0.2.1) (2023-04-18)


### Bug Fixes

* add flask-caching ([7743d05](https://github.com/engisalor/quartz/commit/7743d05db1a296b7c03fb20b7d3cb20724e4e254))
* add mkdir command to get_started ([7313c12](https://github.com/engisalor/quartz/commit/7313c12737af5fd250149a8a6ce820867b6cd605))
* add sidebar footer ([c22a76f](https://github.com/engisalor/quartz/commit/c22a76f0239f299f6ddb372f8627ce3b6edf7637))
* change html.H sizes ([ff01da5](https://github.com/engisalor/quartz/commit/ff01da5fa267c2b10e1341da90591cec56c16aca))
* corpora aio refactor, change html.H sizes ([1ce0985](https://github.com/engisalor/quartz/commit/1ce098571fbf59fa309d342e10058dd90c753e26))
* corpora pie chart responsiveness ([52ee109](https://github.com/engisalor/quartz/commit/52ee109c366cd562612e16f5cc8d71c8953aaaf3))
* freqs graph map title w/ labels ([455c312](https://github.com/engisalor/quartz/commit/455c31260de70e1b7915dda91dfac49cf613569b))
* freqs query order issue ([161d989](https://github.com/engisalor/quartz/commit/161d989079262b22cbab9aba8d03fb9a3cf026aa))
* freqs remove copy_url max size ([7acfe93](https://github.com/engisalor/quartz/commit/7acfe93019e635c1890eea60665cc0650db7c69a))
* frequencies download no data error ([a5db64a](https://github.com/engisalor/quartz/commit/a5db64af0883bfce0c7dce72905ee9361c464883))
* improve responsiveness ([56b56a3](https://github.com/engisalor/quartz/commit/56b56a36e7a5b3c1eb54d876c3f47422d2b308d6))
* remove sgex settings patches ([d9610d8](https://github.com/engisalor/quartz/commit/d9610d8bea1c87b230b63b054e0e96530480e6c5))
* surround PWD in {} ([6a35d75](https://github.com/engisalor/quartz/commit/6a35d7556c5b742326766cf4a27f692b78afce47))
* update icons ([b0efcef](https://github.com/engisalor/quartz/commit/b0efcef4b4325abee1b61d76f5314838648cb493))
* update requirements ([fbea0f2](https://github.com/engisalor/quartz/commit/fbea0f2f798318b39979faa6c5acd4f7ae8a3bc6))

## [0.2.0](https://github.com/engisalor/quartz/compare/v0.1.0...v0.2.0) (2023-03-21)

This release is a major update for the app, with various front- and back-end improvements.

* now uses SGEX v0.6+ for making API calls and caching data
* more mature Frequencies and Corpora pages for data visualization
* simpler setup process to get started
* clearer package structure
* various bug fixes
