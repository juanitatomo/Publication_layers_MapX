<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>Number of people per 250 square meters (2015)</sld:Name>
    <sld:UserStyle>
      <sld:Name>Number of people per 250 square meters (2015)</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
                <sld:ContrastEnhancement>
                  <sld:GammaValue>1.0</sld:GammaValue>
                </sld:ContrastEnhancement>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap>
              <sld:ColorMapEntry color="#fff5f0" quantity="0" label="0"/>
              <sld:ColorMapEntry color="#fee0d2" quantity="5" label="5"/>
              <sld:ColorMapEntry color="#fcbba1" quantity="10" label="10"/>
              <sld:ColorMapEntry color="#fc9272" quantity="15" label="15"/>
              <sld:ColorMapEntry color="#fb6a4a" quantity="20" label="20"/>
              <sld:ColorMapEntry color="#ef3b2c" quantity="25" label="25"/>
              <sld:ColorMapEntry color="#cb181d" quantity="30" label="30"/>
              <sld:ColorMapEntry color="#a50f15" quantity="35" label="35"/>
              <sld:ColorMapEntry color="#67000d" quantity="38" label="&gt; 35"/>
            </sld:ColorMap>
            <sld:ContrastEnhancement/>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>

